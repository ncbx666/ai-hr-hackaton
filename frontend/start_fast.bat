@echo off
REM Быстрый запуск AI-HR Frontend
echo 🚀 Запуск оптимизированного AI-HR Frontend...

REM Переходим в правильную директорию
cd /d "C:\Users\79046\Desktop\ai-hr-hackaton\ai-hr-hackaton\frontend"

REM Останавливаем существующие Node процессы на порту 3000
echo 🛑 Остановка существующих серверов...
for /f "tokens=5" %%a in ('netstat -ano ^| findstr :3000') do taskkill /f /pid %%a >nul 2>&1

REM Устанавливаем переменные для оптимизации
set GENERATE_SOURCEMAP=false
set SKIP_PREFLIGHT_CHECK=true
set FAST_REFRESH=false

REM Проверяем наличие node_modules
if not exist node_modules (
    echo 📦 Установка зависимостей...
    npm install --silent
)

REM Запускаем оптимизированный сервер
echo ⚡ Запуск frontend сервера...
echo 📡 Frontend будет доступен: http://localhost:3000
npm start

pause
