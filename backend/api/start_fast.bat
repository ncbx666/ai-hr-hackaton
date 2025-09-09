@echo off
REM Быстрый запуск AI-HR Backend сервера
echo 🚀 Запуск оптимизированного AI-HR Backend...

REM Переходим в правильную директорию
cd /d "C:\Users\79046\Desktop\ai-hr-hackaton\ai-hr-hackaton\backend\api"

REM Останавливаем любые существующие процессы Python
echo 🛑 Остановка существующих серверов...
taskkill /f /im python.exe >nul 2>&1

REM Ждем немного
timeout /t 2 /nobreak >nul

REM Очищаем кэш Python
echo 🧹 Очистка кэша...
if exist __pycache__ rmdir /s /q __pycache__ >nul 2>&1
if exist .pytest_cache rmdir /s /q .pytest_cache >nul 2>&1

REM Запускаем оптимизированный сервер
echo ⚡ Запуск сервера...
python main_optimized.py

pause
