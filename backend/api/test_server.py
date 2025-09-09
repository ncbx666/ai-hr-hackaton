#!/usr/bin/env python3
"""
Минимальный тестовый сервер для проверки работы API
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

app = FastAPI(title="Test AI-HR Backend")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/api/health")
async def health_check():
    """Проверка работоспособности API"""
    return {"status": "OK", "message": "Test server is running"}

@app.post("/api/hr/interviews")
async def create_interview(interview_data: dict):
    """Создание интервью - тестовая заглушка"""
    return {
        "id": "test-interview-123",
        "status": "created",
        "message": "Test interview created successfully",
        "data": interview_data
    }

@app.post("/api/hr/upload-multi")
async def upload_multi():
    """Загрузка файлов - тестовая заглушка"""
    return {
        "status": "OK",
        "message": "Files uploaded successfully",
        "files": []
    }

if __name__ == "__main__":
    print("🧪 Запуск тестового AI-HR Backend...")
    print("📡 API доступно: http://127.0.0.1:8000")
    print("📖 Документация: http://127.0.0.1:8000/docs")
    
    uvicorn.run(
        app,
        host="127.0.0.1",
        port=8000,
        reload=False
    )
