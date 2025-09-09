# Модель резюме для InterviewCreate
from pydantic import BaseModel
import os
from dotenv import load_dotenv

# Загружаем переменные окружения
load_dotenv()

# Проверяем наличие важных переменных
required_vars = {
    "DATABASE_URL": os.getenv("DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/ai_hr_hackaton"),
    "DEBUG": os.getenv("DEBUG", "True").lower() == "true"
}

print(f"[Config] Database URL: {required_vars['DATABASE_URL']}")
print(f"[Config] Debug mode: {required_vars['DEBUG']}")

class ResumeInfo(BaseModel):
    filename: str
    url: str
from google_sheets import write_result_to_sheet
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
from db import SessionLocal, InterviewDB, ResumeDB, engine
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

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

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
def create_interview(data: InterviewCreate, db: Session = Depends(get_db)):
    print('create_interview called')
    print("[DEBUG] /api/hr/interviews payload:", data)
    try:
        interview_id = str(uuid.uuid4())
        interview_db = InterviewDB(
            id=interview_id,
            position=data.position,
            job_description=data.job_description,
            status="created",
            results_url=None
        )
        db.add(interview_db)
        db.commit()
        db.refresh(interview_db)
        resumes_out = []
        for resume in data.resumes:
            resume_db = ResumeDB(
                filename=resume.filename,
                url=resume.url,
                interview_id=interview_id
            )
            db.add(resume_db)
            resumes_out.append(resume)
        db.commit()
        return Interview(
            id=interview_db.id,
            position=interview_db.position,
            job_description=interview_db.job_description,
            resumes=resumes_out,
            status=interview_db.status,
            results_url=interview_db.results_url
        )
    except Exception as e:
        import traceback
        print("[ERROR] /api/hr/interviews:", e)
        traceback.print_exc()
        from fastapi import HTTPException
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/hr/interviews", response_model=List[Interview])
def list_interviews(db: Session = Depends(get_db)):
    interviews = db.query(InterviewDB).all()
    result = []
    for interview in interviews:
        resumes = db.query(ResumeDB).filter(ResumeDB.interview_id == interview.id).all()
        resumes_out = [ResumeInfo(filename=r.filename, url=r.url) for r in resumes]
        result.append(Interview(
            id=interview.id,
            position=interview.position,
            job_description=interview.job_description,
            resumes=resumes_out,
            status=interview.status,
            results_url=interview.results_url
        ))
    return result

@app.get("/api/hr/results/{interview_id}")
def get_results(interview_id: str, db: Session = Depends(get_db)):
    interview = db.query(InterviewDB).filter(InterviewDB.id == interview_id).first()
    if not interview or not interview.results_url:
        return {"error": "Результаты не найдены"}
    return {"results_url": interview.results_url}

@app.get("/api/hr/requirements/{interview_id}")
def get_requirements(interview_id: str, db: Session = Depends(get_db)):
    interview = db.query(InterviewDB).filter(InterviewDB.id == interview_id).first()
    if not interview:
        return {"error": "Собеседование не найдено"}
    resumes = db.query(ResumeDB).filter(ResumeDB.interview_id == interview_id).all()
    resumes_out = [ResumeInfo(filename=r.filename, url=r.url) for r in resumes]
    return {"job_description": interview.job_description, "resumes": resumes_out}

# WebSocket для интервью
# Временно используем заглушки вместо speech_service
class MockSpeechService:
    async def transcribe_audio(self, audio_data: bytes, is_final: bool = False) -> str:
        return f"[MOCK STT] Обработано {len(audio_data)} байт аудио"
    
    async def generate_speech(self, text: str) -> bytes:
        return b"[MOCK TTS] " + text.encode()

class MockQuestionGenerator:
    async def generate_question(self, transcript: str, question_number: int, job_description: str = "", previous_questions: list = None) -> str:
        return f"Вопрос {question_number}: Расскажите подробнее о вашем опыте в {transcript[:20]}..."

speech_service = MockSpeechService()
question_generator = MockQuestionGenerator()

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
                
                end_message = "Интервью завершено. Начинается автоматическая обработка результатов..."
                await websocket.send_json({
                    "type": "interview_ended",
                    "message": end_message
                })
                
                # Отправляем результат автоматической обработки
                await websocket.send_json({
                    "type": "processing_completed",
                    "processing_result": processing_result
                })
                
                # Генерируем аудио для завершения
                try:
                    final_message = "Спасибо за интервью! Результаты обработаны автоматически."
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
        print("[DEBUG] upload-multi files:", [file.filename for file in files])
        result = []
        for file in files:
            file_location = os.path.join(UPLOAD_DIR, file.filename)
            with open(file_location, "wb") as f:
                content = await file.read()
                f.write(content)
            result.append({
                "filename": file.filename,
                "url": f"/api/hr/file/{file.filename}"
            })
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
        write_result_to_sheet(score_data)
    except Exception as e:
        print(f"Ошибка записи в Google Sheets: {e}")
    return score_data

if __name__ == "__main__":
    import uvicorn
    print("🚀 Запуск AI-HR Backend сервера...")
    print("📡 API будет доступно по адресу: http://localhost:8000")
    print("📖 Документация: http://localhost:8000/docs")
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
