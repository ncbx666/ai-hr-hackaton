# AI-HR Система автоматизированного собеседования

Система для проведения автоматизированных собеседований с использованием ИИ, включающая веб-интерфейс для HR-специалистов и кандидатов, голосовое взаимодействие и интеграцию с ML моделями.

## Ключевые функции

* **Генерация вопросов:** ИИ-модель создаёт вопросы для собеседования на основе описания вакансии и резюме
* **Голосовое интервью:** WebSocket-соединение для реального времени общения с кандидатом  
* **Распознавание речи:** Google STT для преобразования голоса в текст
* **Синтез речи:** Google TTS для голосовых ответов системы
* **Автоматическая оценка:** ML-модели для оценки кандидата по ключевым критериям
* **HR Dashboard:** Веб-интерфейс для создания собеседований и просмотра результатов
* **Интеграция с Google Sheets:** Экспорт результатов для дальнейшего анализа

## Архитектура системы

### Frontend (React + TypeScript)
- HR Dashboard для создания собеседований
- Интерфейс кандидата с голосовым взаимодействием
- WebSocket клиент для реального времени

### Backend (FastAPI + Python)  
- REST API для управления собеседованиями
- WebSocket сервер для голосового интервью
- Интеграция с Google STT/TTS
- PostgreSQL база данных
- ML модели для генерации вопросов и оценки

### Используемые технологии

* **AI Models:** Gemini 2.5 Flash, OpenAI GPT
* **Backend:** FastAPI, Python, SQLAlchemy, WebSockets
* **Frontend:** React, TypeScript, CSS3
* **Database:** PostgreSQL
* **Google Services:** Speech-to-Text, Text-to-Speech, Sheets API
* **Real-time:** WebSocket connections

## Быстрый старт

### 1. Запуск Backend
```bash
cd backend
pip install fastapi uvicorn python-multipart python-dotenv sqlalchemy psycopg2-binary
python -m uvicorn api.main:app --host 0.0.0.0 --port 8000 --reload
```

### 2. Запуск Frontend  
```bash
cd frontend
npm install
PORT=3001 npm start  # если порт 3000 занят
```

### 3. Открыть в браузере
- Frontend: http://localhost:3001
- Backend API: http://localhost:8000
- WebSocket: ws://localhost:8000/ws/interview/{session_id}

## Текущий статус

✅ **Реализовано:**
- Веб-интерфейс для HR и кандидатов
- WebSocket соединение для реального времени
- Базовая обработка аудио  
- PostgreSQL интеграция
- CSS стилизация
- Mock сервисы для тестирования

🔄 **В разработке:**
- Интеграция с Google STT/TTS
- ML модели для генерации вопросов
- Система скоринга

🚀 **Планируется:**
- Google Sheets экспорт
- Аутентификация
- Видео интервью
