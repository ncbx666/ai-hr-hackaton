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

# Running the AI-HR System

## Prerequisites
- Python 3.8 or higher
- Node.js 14 or higher
- pip (Python package manager)
- npm (Node package manager)

## Running the System

### Option 1: Run Backend and Frontend Separately

#### Backend
1. Navigate to the backend directory:
   ```
   cd ai-hr-hackaton/backend/api
   ```
2. Run the backend server:
   ```
   python main_optimized.py
   ```
3. The backend will be available at: http://127.0.0.1:8000
4. API documentation: http://127.0.0.1:8000/docs

#### Using Combined Script
1. Run both services together:
   ```
   ai-hr-hackaton/start_all.bat
   ```

## Accessing the Application
- Frontend: http://localhost:3000
- Backend API: http://127.0.0.1:8000
- Backend API Documentation: http://127.0.0.1:8000/docs

## Troubleshooting
1. If you encounter path issues, make sure you're running the scripts from the correct directory
2. If ports are already in use, you may need to stop existing processes:
   - Backend: `taskkill /f /im python.exe`
   - Frontend: `taskkill /f /im node.exe`
3. If dependencies are missing, install them:
   - Backend: `pip install -r requirements.txt` (in backend directory)
   - Frontend: `npm install` (in frontend directory)
