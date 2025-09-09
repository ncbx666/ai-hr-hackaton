# Модель резюме для InterviewCreate
from pydantic import BaseModel
import os
from dotenv import load_dotenv

# Загружаем переменные окружения
load_dotenv()

# Импортируем переменные из db.py (временно отключено для простого тестирования)
#from db import SessionLocal, InterviewDB, ResumeDB, engine, DATABASE_URL

# Проверяем наличие важных переменных
required_vars = {
    "DATABASE_URL": "sqlite:///./ai_hr_hackaton.db",  # Временно хардкод
    "DEBUG": os.getenv("DEBUG", "True").lower() == "true"
}

print(f"[Config] Database URL: {required_vars['DATABASE_URL']}")
print(f"[Config] Debug mode: {required_vars['DEBUG']}")

class ResumeInfo(BaseModel):
    filename: str
    url: str

from google_sheets import google_sheets_service
from monitoring_endpoints import router as monitoring_router
import subprocess
import tempfile
from fastapi import FastAPI, UploadFile, File, WebSocket, WebSocketDisconnect, Depends
from fastapi.middleware.cors import CORSMiddleware
import json
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import List, Optional
import uuid
from sqlalchemy.orm import Session
from interview_processor import auto_processor
from datetime import datetime



import os
import base64
UPLOAD_DIR = os.path.join(os.path.dirname(__file__), "uploads")
os.makedirs(UPLOAD_DIR, exist_ok=True)



app = FastAPI()

# CORS settings
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:3001", "http://localhost:3002"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

# Импорт и обработчики ошибок строго после app = FastAPI()
from fastapi.requests import Request
from fastapi.responses import JSONResponse
from fastapi.exception_handlers import RequestValidationError
from fastapi.exceptions import RequestValidationError as RVError
import traceback

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    print("[GLOBAL ERROR] Exception:", exc)
    traceback.print_exc()
    return JSONResponse(status_code=500, content={"detail": str(exc)})

@app.exception_handler(RVError)
async def validation_exception_handler(request: Request, exc: RVError):
    print("[GLOBAL ERROR] ValidationError:", exc)
    traceback.print_exc()
    return JSONResponse(status_code=422, content={"detail": exc.errors()})

# Глобальный обработчик ошибок
from fastapi.requests import Request
from fastapi.responses import JSONResponse
from fastapi.exception_handlers import RequestValidationError
from fastapi.exceptions import RequestValidationError as RVError
import traceback

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    print("[GLOBAL ERROR] Exception:", exc)
    traceback.print_exc()
    return JSONResponse(status_code=500, content={"detail": str(exc)})

@app.exception_handler(RVError)
async def validation_exception_handler(request: Request, exc: RVError):
    print("[GLOBAL ERROR] ValidationError:", exc)
    traceback.print_exc()
    return JSONResponse(status_code=422, content={"detail": exc.errors()})

# Временно отключаем get_db для простого тестирования
# def get_db():
#     db = SessionLocal()
#     try:
#         yield db
#     finally:
#         db.close()

# Модели
class ResumeInfo(BaseModel):
    filename: str
    url: str

class InterviewCreate(BaseModel):
    position: str
    job_description: str
    resumes: List[ResumeInfo]

class Interview(BaseModel):
    id: str
    position: str
    job_description: str
    resumes: List[ResumeInfo]
    status: str
    results_url: Optional[str]



@app.post("/api/hr/interviews", response_model=Interview)
async def create_interview(data: InterviewCreate):
    print(f'[DEBUG] create_interview called with data: {data}')
    print(f"[DEBUG] /api/hr/interviews payload: {data}")
    try:
        interview_id = str(uuid.uuid4())
        print(f"[DEBUG] Generated interview_id: {interview_id}")
        
        # Временно без базы данных - для тестирования
        resumes_out = []
        for resume in data.resumes:
            print(f"[DEBUG] Processing resume: {resume}")
            resumes_out.append(ResumeInfo(
                filename=resume.filename,
                url=resume.url
            ))
        
        print(f"[DEBUG] Processed resumes: {resumes_out}")
        
        # Создаем Google таблицу для интервью
        interview_data = {
            'id': interview_id,
            'position': data.position,
            'job_description': data.job_description,
            'created_at': datetime.now().isoformat()
        }
        
        print(f"[DEBUG] Creating Google Sheet with data: {interview_data}")
        
        try:
            google_sheets_url = await google_sheets_service.create_interview_sheet(interview_data)
            print(f"[SUCCESS] Google Sheet created: {google_sheets_url}")
        except Exception as e:
            print(f"[WARNING] Failed to create Google Sheet: {e}")
            google_sheets_url = f"https://docs.google.com/spreadsheets/d/demo_{interview_id}/edit"
        
        interview = Interview(
            id=interview_id,
            position=data.position,
            job_description=data.job_description,
            resumes=resumes_out,
            status="created",
            results_url=google_sheets_url  # Используем Google Sheets URL как results_url
        )
        
        print(f"[SUCCESS] Interview created: {interview_id}")
        print(f"[SUCCESS] Results URL: {google_sheets_url}")
        print(f"[DEBUG] Returning interview object: {interview}")
        return interview
        
    except Exception as e:
        import traceback
        print("[ERROR] /api/hr/interviews:", e)
        traceback.print_exc()
        from fastapi import HTTPException
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/hr/interviews", response_model=List[Interview])
async def list_interviews():
    """Возвращает список всех интервью включая завершенные"""
    result = []
    
    # Добавляем завершенные интервью
    for completed in completed_interviews:
        result.append(Interview(
            id=completed["id"],
            position=completed["position"],
            job_description=completed.get("job_description", "Generated from session"),
            resumes=[ResumeInfo(filename="session_data.json", url=f"/session/{completed['id']}")],
            status=completed["status"],
            results_url=f"https://docs.google.com/spreadsheets/d/demo_{completed['id']}/edit"
        ))
    
    # Добавляем активные сессии как созданные интервью
    for session_id, session in active_sessions.items():
        if session.is_active:
            result.append(Interview(
                id=session_id,
                position=session.job_description or "Interview in Progress",
                job_description=session.job_description,
                resumes=[ResumeInfo(filename="session_data.json", url=f"/session/{session_id}")],
                status="in_progress",
                results_url=None
            ))
    
    return result

@app.get("/api/hr/results/{interview_id}")
async def get_results(interview_id: str):
    """Получение ссылки на Google таблицу с результатами"""
    try:
        # Ищем в завершенных интервью
        for completed in completed_interviews:
            if completed["id"] == interview_id:
                return {
                    "results_url": f"https://docs.google.com/spreadsheets/d/demo_{interview_id}/edit",
                    "interview_id": interview_id,
                    "status": "completed",
                    "candidate_name": completed.get("candidateName", "Unknown"),
                    "score": completed.get("score", 0),
                    "processing_result": completed.get("processing_result")
                }
        
        # Если не найден, пытаемся получить из Google Sheets сервиса
        google_sheets_url = await google_sheets_service.get_interview_sheet_url(interview_id)
        if google_sheets_url:
            return {
                "results_url": google_sheets_url,
                "interview_id": interview_id,
                "status": "available"
            }
        else:
            return {
                "results_url": f"https://docs.google.com/spreadsheets/d/demo_{interview_id}/edit",
                "interview_id": interview_id,
                "status": "demo"
            }
    except Exception as e:
        print(f"[ERROR] Error getting results for {interview_id}: {e}")
        return {
            "results_url": f"https://docs.google.com/spreadsheets/d/demo_{interview_id}/edit",
            "interview_id": interview_id,
            "status": "error"
        }

@app.get("/api/hr/requirements/{interview_id}")
def get_requirements(interview_id: str):
    # Временно возвращаем mock данные
    return {
        "job_description": "Mock job description", 
        "resumes": [{"filename": "sample.pdf", "url": "/sample.pdf"}]
    }

# WebSocket для интервью
# Импортируем реальные сервисы
from speech_service import SpeechService, MLQuestionGenerator

<<<<<<< HEAD
class QuestionGenerator:
    def __init__(self):
        # Добавляем путь к ds1 для импорта модуля
        import sys
        import os
        sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))
        
        # Получаем API ключ из переменных окружения
        self.api_key = os.getenv("GOOGLE_API_KEY")
        if not self.api_key:
            print("WARNING: GOOGLE_API_KEY не найден в переменных окружения")
            self.api_key = "PLACEHOLDER_API_KEY"  # Заглушка для тестирования
    
    async def generate_question(self, transcript: str, question_number: int, job_description: str = "", previous_questions: list = None) -> str:
        try:
            # Импортируем функцию генерации вопросов
            from ds1.generate_questions import generate_next_questions
            
            # Подготавливаем данные для генерации
            # В реальной реализации здесь должна быть логика извлечения данных резюме
            # из контекста сессии или базы данных
            resume_data = {
                "responsibilities": [],
                "experience": [],
                "skills": []
            }
            
            vacancy_data = {
                "vacancy_info": {
                    "duties": job_description,
                    "responsibilities": job_description,
                    "requirements": "",
                    "skills": []
                }
            }
            
            # Формируем предыдущие вопросы и ответы
            previous_qa = []
            if previous_questions and len(previous_questions) > 0:
                # Берем последний вопрос как текущий
                previous_qa = [
                    {
                        "question": previous_questions[-1] if previous_questions else "Предыдущий вопрос",
                        "answer": transcript
                    }
                ]
            
            # Генерируем следующие вопросы
            questions = generate_next_questions(resume_data, vacancy_data, previous_qa, self.api_key)
            
            # Возвращаем первый сгенерированный вопрос
            if questions and len(questions) > 0:
                # Проверяем, не является ли это ошибкой
                if isinstance(questions, list) and len(questions) > 0:
                    first_question = questions[0]
                    if isinstance(first_question, dict) and "action" in first_question:
                        if first_question["action"] == "error":
                            print(f"[QuestionGenerator] Ошибка генерации: {first_question.get('rationale', '')}")
                            return "Не удалось сгенерировать вопрос. Расскажите подробнее о своем опыте."
                        elif first_question["action"] == "ask_general":
                            return first_question.get("question", "Расскажите подробнее о вашем опыте.")
                        else:
                            return first_question.get("question", "Расскажите подробнее о вашем опыте.")
                    else:
                        return first_question.get("question", "Расскажите подробнее о вашем опыте.")
                else:
                    return str(questions[0]) if len(str(questions[0])) > 0 else "Расскажите подробнее о вашем опыте."
            else:
                return "Расскажите подробнее о вашем опыте."
                
        except Exception as e:
            print(f"[QuestionGenerator] Ошибка генерации вопроса: {e}")
            import traceback
            traceback.print_exc()
            return "Не удалось сгенерировать вопрос. Расскажите подробнее о своем опыте."

# Создаем экземпляр генератора вопросов
question_generator = QuestionGenerator()

speech_service = MockSpeechService()
=======
# Инициализируем реальные сервисы
speech_service = SpeechService()
question_generator = MLQuestionGenerator()
>>>>>>> fd9c1e3a04caefd684cd8abbd9c2b1a1516b0d68

class InterviewSession:
    def __init__(self, session_id: str, job_description: str = ""):
        self.session_id = session_id
        self.job_description = job_description
        self.transcript_buffer = ""
        self.question_count = 0
        self.is_active = True
        self.previous_questions = []
        self.candidate_answers = []  # Добавляем для сохранения ответов
        self.candidate_name = "Unknown"  # Добавляем имя кандидата
        self.interview_start_time = None
        self.interview_end_time = None
        
    async def process_audio_chunk(self, audio_data: bytes) -> str:
        """Обработка аудио через Google STT"""
        try:
            # Декодируем base64 если нужно
            if isinstance(audio_data, str):
                audio_data = base64.b64decode(audio_data)
            
            # Транскрипция через Google STT
            transcript = await speech_service.transcribe_audio(audio_data, is_final=False)
            return transcript
        except Exception as e:
            print(f"[InterviewSession] Audio processing error: {e}")
            return f"[Ошибка обработки аудио]: {str(e)}"
        
    async def add_candidate_answer(self, answer: str):
        """Добавляет ответ кандидата в историю"""
        self.candidate_answers.append(answer)
        self.transcript_buffer += f" {answer}"
        
    async def generate_question(self, transcript: str) -> str:
        """Генерация вопроса через ML модели"""
        try:
            self.question_count += 1
            
            # Добавляем ответ в буфер и историю
            await self.add_candidate_answer(transcript)
            
            # Генерируем вопрос через ML
            question = await question_generator.generate_question(
                transcript=transcript,
                question_number=self.question_count,
                job_description=self.job_description,
                previous_questions=self.previous_questions
            )
            
            # Сохраняем вопрос в историю
            self.previous_questions.append(question)
            
            return question
        except Exception as e:
            print(f"[InterviewSession] Question generation error: {e}")
            return f"Не удалось сгенерировать вопрос. Расскажите подробнее о своем опыте."
    
    async def end_interview(self):
        """Завершает интервью и запускает автоматическую обработку"""
        self.is_active = False
        self.interview_end_time = datetime.now()
        
        # Запускаем автоматическую обработку
        try:
            processing_result = await auto_processor.process_completed_interview(self)
            print(f"[InterviewSession] Автоматическая обработка завершена: {processing_result}")
            return processing_result
        except Exception as e:
            print(f"[InterviewSession] Ошибка автоматической обработки: {e}")
            return {"error": str(e)}
    
    async def generate_audio_response(self, text: str) -> bytes:
        """Генерация аудио ответа через Google TTS"""
        try:
            audio_data = await speech_service.generate_speech(text)
            return audio_data
        except Exception as e:
            print(f"[InterviewSession] TTS error: {e}")
            return b""

# Храним активные сессии
active_sessions = {}

# Храним завершенные интервью
completed_interviews = []

@app.websocket("/ws/interview/{session_id}")
async def interview_ws(websocket: WebSocket, session_id: str, job_description: str = ""):
    await websocket.accept()
    print(f"[WebSocket] Подключение {session_id}")
    
    # Создаём или получаем сессию
    if session_id not in active_sessions:
        active_sessions[session_id] = InterviewSession(session_id, job_description)
        active_sessions[session_id].interview_start_time = datetime.now()
    
    session = active_sessions[session_id]
    
    try:
        # Отправляем приветственное сообщение
        welcome_message = "Добро пожаловать на собеседование! Представьтесь, пожалуйста."
        await websocket.send_json({
            "type": "welcome",
            "message": welcome_message
        })
        
        # Генерируем аудио для приветствия
        try:
            audio_data = await session.generate_audio_response(welcome_message)
            if audio_data:
                import base64
                audio_base64 = base64.b64encode(audio_data).decode()
                await websocket.send_json({
                    "type": "audio_response",
                    "audio_data": audio_base64,
                    "text": welcome_message
                })
        except Exception as e:
            print(f"[WebSocket] TTS error: {e}")
        
        while session.is_active:
            # Принимаем данные от клиента
            message = await websocket.receive_json()
            
            if message["type"] == "audio_chunk":
                # Обрабатываем аудио через STT
                audio_data = message.get("data", "")
                transcript = await session.process_audio_chunk(audio_data)
                
                # Отправляем промежуточный транскрипт
                if transcript and not transcript.startswith("["):
                    await websocket.send_json({
                        "type": "transcript",
                        "text": transcript,
                        "is_final": False
                    })
                
            elif message["type"] == "final_transcript":
                # Финальный транскрипт - генерируем вопрос
                final_text = message.get("text", "")
                
                if final_text.strip():
                    # Отправляем финальный транскрипт
                    await websocket.send_json({
                        "type": "transcript",
                        "text": final_text,
                        "is_final": True
                    })
                    
                    # Генерируем и отправляем вопрос
                    question = await session.generate_question(final_text)
                    await websocket.send_json({
                        "type": "question",
                        "text": question,
                        "question_number": session.question_count
                    })
                    
                    # Генерируем аудио ответ
                    try:
                        audio_data = await session.generate_audio_response(question)
                        if audio_data:
                            audio_base64 = base64.b64encode(audio_data).decode()
                            await websocket.send_json({
                                "type": "audio_response",
                                "audio_data": audio_base64,
                                "text": question
                            })
                    except Exception as e:
                        print(f"[WebSocket] TTS error for question: {e}")
                
            elif message["type"] == "candidate_info":
                # Получаем информацию о кандидате
                session.candidate_name = message.get("name", "Unknown")
                await websocket.send_json({
                    "type": "info_received",
                    "message": f"Добро пожаловать, {session.candidate_name}!"
                })
                
            elif message["type"] == "end_interview":
                # Завершаем интервью и запускаем автоматическую обработку
                processing_result = await session.end_interview()
                
                # Добавляем завершенное интервью в список
                completed_interview = {
                    "id": session_id,
                    "candidateName": session.candidate_name,
                    "position": session.job_description or "Unknown Position",
                    "status": "completed",
                    "createdAt": session.interview_start_time.strftime("%Y-%m-%d") if session.interview_start_time else datetime.now().strftime("%Y-%m-%d"),
                    "score": processing_result.get("score_data", {}).get("final_score_percent", 0) if processing_result.get("success") else 0,
                    "processing_result": processing_result
                }
                completed_interviews.append(completed_interview)
                
                end_message = "Интервью завершено. Начинается автоматическая обработка результатов..."
                await websocket.send_json({
                    "type": "interview_ended",
                    "message": end_message
                })
                
                # Отправляем результат автоматической обработки с ссылкой на Google Sheets
                try:
                    google_sheets_url = await google_sheets_service.get_interview_sheet_url(session_id)
                    if not google_sheets_url:
                        google_sheets_url = f"https://docs.google.com/spreadsheets/d/demo_{session_id}/edit"
                except:
                    google_sheets_url = f"https://docs.google.com/spreadsheets/d/demo_{session_id}/edit"
                
                await websocket.send_json({
                    "type": "processing_completed",
                    "processing_result": processing_result,
                    "results_url": google_sheets_url,
                    "redirect_to": f"/hr/results?interview_id={session_id}"
                })
                
                # Генерируем аудио для завершения
                try:
                    final_message = "Спасибо за интервью! Результаты обработаны автоматически и сохранены в Google таблице."
                    audio_data = await session.generate_audio_response(final_message)
                    if audio_data:
                        audio_base64 = base64.b64encode(audio_data).decode()
                        await websocket.send_json({
                            "type": "audio_response",
                            "audio_data": audio_base64,
                            "text": final_message
                        })
                except Exception as e:
                    print(f"[WebSocket] TTS error for end: {e}")
                
                break
                
    except WebSocketDisconnect:
        print(f"[WebSocket] Отключение {session_id}")
    except Exception as e:
        print(f"[WebSocket] Error in session {session_id}: {e}")
        import traceback
        traceback.print_exc()
    finally:
        # Очищаем сессию при отключении
        if session_id in active_sessions:
            del active_sessions[session_id]


# Множественная загрузка файлов
@app.post("/api/hr/upload-multi")
async def upload_files(files: List[UploadFile] = File(...)):
    try:
        print(f"[DEBUG] upload-multi called with {len(files)} files")
        print("[DEBUG] upload-multi files:", [file.filename for file in files])
        result = []
        for file in files:
            print(f"[DEBUG] Processing file: {file.filename}, content_type: {file.content_type}")
            file_location = os.path.join(UPLOAD_DIR, file.filename)
            with open(file_location, "wb") as f:
                content = await file.read()
                f.write(content)
                print(f"[DEBUG] File saved: {file_location}, size: {len(content)} bytes")
            result.append({
                "filename": file.filename,
                "url": f"/api/hr/file/{file.filename}"
            })
        print(f"[DEBUG] upload-multi result: {result}")
        return {"files": result}
    except Exception as e:
        import traceback
        print("[ERROR] /api/hr/upload-multi:", e)
        traceback.print_exc()
        from fastapi import HTTPException
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/hr/file/{filename}")
def get_uploaded_file(filename: str):
    file_location = os.path.join(UPLOAD_DIR, filename)
    if not os.path.exists(file_location):
        return {"error": "Файл не найден"}
    return FileResponse(file_location, media_type="application/octet-stream", filename=filename)

# Тестовый эндпоинт для проверки Google Sheets
@app.get("/api/test/google-sheets")
async def test_google_sheets():
    """Тестовый эндпоинт для проверки Google Sheets интеграции"""
    try:
        print("[DEBUG] Testing Google Sheets service...")
        
        # Тестовые данные для создания таблицы
        test_interview_data = {
            'id': 'test_interview_123',
            'position': 'Test Frontend Developer',
            'job_description': 'Test job description for frontend role',
            'created_at': datetime.now().isoformat()
        }
        
        # Тестируем создание таблицы
        sheets_url = await google_sheets_service.create_interview_sheet(test_interview_data)
        print(f"[DEBUG] Google Sheets URL created: {sheets_url}")
        
        # Тестируем обновление результатов
        test_results_data = {
            'candidate_name': 'Тестовый Кандидат',
            'final_score_percent': 85,
            'verdict': 'Рекомендуется к найму',
            'breakdown': {
                'hard_skills': {'score_percent': 90},
                'experience': {'score_percent': 80},
                'soft_skills': {'score_percent': 85}
            }
        }
        
        update_result = await google_sheets_service.update_interview_results('test_interview_123', test_results_data)
        print(f"[DEBUG] Google Sheets update result: {update_result}")
        
        # Тестируем получение URL
        retrieved_url = await google_sheets_service.get_interview_sheet_url('test_interview_123')
        print(f"[DEBUG] Retrieved Google Sheets URL: {retrieved_url}")
        
        return {
            "status": "success",
            "message": "Google Sheets integration working",
            "sheets_url": sheets_url,
            "update_success": update_result,
            "retrieved_url": retrieved_url
        }
        
    except Exception as e:
        import traceback
        print(f"[ERROR] Google Sheets test failed: {e}")
        traceback.print_exc()
        return {
            "status": "error", 
            "message": f"Google Sheets test failed: {str(e)}"
        }

# Эндпоинты для мониторинга Google Sheets
@app.get("/api/debug/google-sheets/logs")
async def get_google_sheets_logs(limit: int = 20):
    """Получить логи операций Google Sheets"""
    try:
        logs = google_sheets_service.get_operation_logs(limit)
        return {
            "status": "success",
            "total_logs": len(logs),
            "logs": logs
        }
    except Exception as e:
        return {
            "status": "error",
            "message": f"Ошибка получения логов: {str(e)}"
        }

@app.get("/api/debug/google-sheets/errors")
async def get_google_sheets_errors(limit: int = 10):
    """Получить логи ошибок Google Sheets"""
    try:
        errors = google_sheets_service.get_error_logs(limit)
        return {
            "status": "success",
            "total_errors": len(errors),
            "errors": errors
        }
    except Exception as e:
        return {
            "status": "error",
            "message": f"Ошибка получения логов ошибок: {str(e)}"
        }

@app.get("/api/debug/google-sheets/stats")
async def get_google_sheets_statistics():
    """Получить статистику операций Google Sheets"""
    try:
        stats = google_sheets_service.get_statistics()
        return {
            "status": "success",
            "statistics": stats
        }
    except Exception as e:
        return {
            "status": "error",
            "message": f"Ошибка получения статистики: {str(e)}"
        }

@app.post("/api/debug/google-sheets/clear-logs")
async def clear_google_sheets_logs():
    """Очистить логи Google Sheets (для отладки)"""
    try:
        google_sheets_service.operation_log.clear()
        google_sheets_service.error_log.clear()
        return {
            "status": "success",
            "message": "Логи очищены"
        }
    except Exception as e:
        return {
            "status": "error",
            "message": f"Ошибка очистки логов: {str(e)}"
        }

@app.get("/debug/google-sheets")
async def google_sheets_monitor():
    """Страница мониторинга Google Sheets"""
    try:
        with open("google_sheets_monitor.html", "r", encoding="utf-8") as f:
            html_content = f.read()
        from fastapi.responses import HTMLResponse
        return HTMLResponse(content=html_content)
    except Exception as e:
        return {"error": f"Не удалось загрузить страницу мониторинга: {str(e)}"}

# Заглушки для хранения

@app.get("/api/interview/{session_id}/results")
async def get_interview_results(session_id: str):
    """Получить результаты обработки интервью"""
    try:
        # Ищем файлы результатов для данной сессии
        from pathlib import Path
        uploads_dir = Path("uploads")
        
        # Ищем транскрипт
        transcript_files = list(uploads_dir.glob(f"transcripts/transcript_{session_id}_*.json"))
        if not transcript_files:
            return {"error": "Транскрипт не найден"}
        
        transcript_file = transcript_files[0]
        
        # Ищем результат скоринга
        score_file = str(transcript_file).replace(".json", "_score.json")
        
        result = {"session_id": session_id}
        
        # Читаем транскрипт
        with open(transcript_file, 'r', encoding='utf-8') as f:
            result["transcript"] = json.load(f)
        
        # Читаем скоринг если есть
        if Path(score_file).exists():
            with open(score_file, 'r', encoding='utf-8') as f:
                result["scoring"] = json.load(f)
        else:
            result["scoring"] = {"status": "pending"}
        
        return result
        
    except Exception as e:
        return {"error": f"Ошибка получения результатов: {str(e)}"}

@app.post("/api/hr/score")
async def score_candidate(data: dict):
    # Сохраняем входные данные во временный файл
    with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".json") as f:
        json.dump(data, f)
        input_path = f.name
    output_path = input_path.replace(".json", "_score.json")
    # Запускаем скоринг-скрипт
    result = subprocess.run([
        "python", "../../ds3/score_candidate.py", input_path, output_path
    ], capture_output=True, text=True)
    if result.returncode != 0:
        return {"error": "Ошибка скоринга", "details": result.stderr}
    # Читаем результат
    with open(output_path, "r") as f:
        score_data = json.load(f)
    # Записываем результат в Google Sheets
    try:
        await google_sheets_service.update_interview_results(
            interview_id="current_interview",  # В реальности здесь ID из контекста
            results_data=score_data
        )
    except Exception as e:
        print(f"Ошибка записи в Google Sheets: {e}")
    return score_data

# Регистрируем роутер мониторинга Google Sheets
app.include_router(monitoring_router)

if __name__ == "__main__":
    import uvicorn
    print("🚀 Запуск AI-HR Backend сервера...")
    print("📡 API будет доступно по адресу: http://localhost:8000")
    print("📖 Документация: http://localhost:8000/docs")
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
