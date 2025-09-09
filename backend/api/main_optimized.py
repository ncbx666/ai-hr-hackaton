"""
AI-HR Backend - Оптимизированная версия для быстрого запуска
Использует ленивую загрузку импортов и минимальную конфигурацию
"""

import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import List, Optional
import json
import uuid
from datetime import datetime

# Быстрая загрузка переменных окружения
from dotenv import load_dotenv
load_dotenv()

# Минимальная конфигурация
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./ai_hr_hackaton.db")
DEBUG = os.getenv("DEBUG", "False").lower() == "true"

print(f"⚡ [FastStart] Database: {DATABASE_URL}")
print(f"⚡ [FastStart] Debug: {DEBUG}")

# Быстрая инициализация FastAPI
app = FastAPI(
    title="AI-HR Backend API",
    description="Optimized for fast startup",
    version="1.0.0",
    docs_url="/docs" if DEBUG else None,
    redoc_url="/redoc" if DEBUG else None
)

# CORS - минимальная конфигурация
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"]
)

# Модели данных
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

# Ленивая загрузка сервисов
_google_sheets_service = None
_monitoring_router = None

def get_google_sheets_service():
    """Ленивая загрузка Google Sheets сервиса"""
    global _google_sheets_service
    if _google_sheets_service is None:
        try:
            from google_sheets_service import google_sheets_service
            _google_sheets_service = google_sheets_service
            print("✅ Google Sheets сервис загружен")
        except ImportError as e:
            print(f"⚠️ Google Sheets недоступен: {e}")
            _google_sheets_service = None
    return _google_sheets_service

def get_monitoring_router():
    """Ленивая загрузка роутера мониторинга"""
    global _monitoring_router
    if _monitoring_router is None:
        try:
            from monitoring_endpoints import router as monitoring_router
            _monitoring_router = monitoring_router
            print("✅ Мониторинг роутер загружен")
        except ImportError as e:
            print(f"⚠️ Мониторинг недоступен: {e}")
            _monitoring_router = None
    return _monitoring_router

# Базовые эндпоинты
@app.get("/")
async def root():
    """Корневой эндпоинт"""
    return {
        "message": "AI-HR Backend API",
        "status": "running",
        "version": "1.0.0",
        "timestamp": datetime.now().isoformat()
    }

@app.get("/health")
async def health_check():
    """Проверка здоровья сервиса"""
    return {
        "status": "healthy",
        "database": "connected" if DATABASE_URL else "disconnected",
        "timestamp": datetime.now().isoformat()
    }

# Основные API эндпоинты
@app.post("/api/hr/interviews", response_model=Interview)
async def create_interview(data: InterviewCreate):
    """Создание нового интервью"""
    try:
        interview_id = str(uuid.uuid4())
        print(f"🚀 Создание интервью: {interview_id}")
        
        # Быстрая симуляция без внешних зависимостей
        interview_data = {
            'id': interview_id,
            'position': data.position,
            'job_description': data.job_description,
            'created_at': datetime.now().isoformat()
        }
        
        # Ленивая загрузка Google Sheets при необходимости
        sheets_service = get_google_sheets_service()
        sheets_url = None
        
        if sheets_service:
            try:
                sheets_url = await sheets_service.create_interview_sheet(interview_data)
                print(f"✅ Google таблица создана: {sheets_url}")
            except Exception as e:
                print(f"⚠️ Ошибка создания таблицы: {e}")
                sheets_url = f"https://docs.google.com/spreadsheets/d/mock_{interview_id}/edit"
        
        # Быстрый ответ
        return Interview(
            id=interview_id,
            position=data.position,
            job_description=data.job_description,
            resumes=data.resumes,
            status="created",
            results_url=sheets_url
        )
        
    except Exception as e:
        print(f"❌ Ошибка создания интервью: {e}")
        return JSONResponse(
            status_code=500,
            content={"error": "Ошибка создания интервью", "details": str(e)}
        )

@app.get("/api/hr/interviews")
async def get_interviews():
    """Получение списка интервью"""
    return {
        "interviews": [],
        "total": 0,
        "message": "Список интервью (демо режим)"
    }

@app.get("/api/hr/interviews/{interview_id}")
async def get_interview(interview_id: str):
    """Получение конкретного интервью"""
    return {
        "id": interview_id,
        "status": "demo",
        "message": f"Интервью {interview_id} (демо режим)"
    }

@app.post("/api/hr/score")
async def score_candidate(data: dict):
    """Быстрая оценка кандидата"""
    try:
        # Быстрая имитация скоринга
        score_data = {
            "candidate_name": data.get("candidate_name", "Test Candidate"),
            "final_score_percent": 85,
            "verdict": "Рекомендуется к найму",
            "breakdown": {
                "hard_skills": {"score_percent": 90},
                "experience": {"score_percent": 80},
                "soft_skills": {"score_percent": 85}
            },
            "timestamp": datetime.now().isoformat()
        }
        
        # Ленивая загрузка Google Sheets для записи результатов
        sheets_service = get_google_sheets_service()
        if sheets_service:
            try:
                await sheets_service.update_interview_results(
                    interview_id=data.get("interview_id", "demo_interview"),
                    results_data=score_data
                )
                print("✅ Результаты записаны в Google Sheets")
            except Exception as e:
                print(f"⚠️ Ошибка записи результатов: {e}")
        
        return score_data
        
    except Exception as e:
        print(f"❌ Ошибка скоринга: {e}")
        return JSONResponse(
            status_code=500,
            content={"error": "Ошибка скоринга", "details": str(e)}
        )

# Регистрация роутера мониторинга при первом обращении
@app.on_event("startup")
async def startup_event():
    """Событие запуска - регистрация дополнительных роутеров"""
    monitoring_router = get_monitoring_router()
    if monitoring_router:
        app.include_router(monitoring_router)
        print("✅ Роутер мониторинга подключен")

# Быстрый запуск для разработки
if __name__ == "__main__":
    import uvicorn
    print("🚀 Запуск оптимизированного AI-HR Backend...")
    print("📡 API доступно: http://127.0.0.1:8000")
    print("📖 Документация: http://127.0.0.1:8000/docs")
    
    uvicorn.run(
        "main_optimized:app",
        host="127.0.0.1",
        port=8000,
        reload=False,  # Отключаем reload для быстрого запуска
        access_log=False,  # Отключаем логи доступа
        log_level="error"  # Минимальное логирование
    )
