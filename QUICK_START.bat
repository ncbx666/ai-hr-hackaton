@echo off
title AI-HR Quick Start
color 0A
echo.
echo  ██████╗ ██╗       ██╗  ██╗██████╗ 
echo ██╔═══██╗██║       ██║  ██║██╔══██╗
echo ██║   ██║██║ █████╗███████║██████╔╝
echo ██║   ██║██║ ╚════╝██╔══██║██╔══██╗
echo ╚██████╔╝██║       ██║  ██║██║  ██║
echo  ╚═════╝ ╚═╝       ╚═╝  ╚═╝╚═╝  ╚═╝
echo.
echo ⚡ БЫСТРЫЙ ЗАПУСК AI-HR СИСТЕМЫ ⚡
echo.

set PROJECT_ROOT=C:\Users\79046\Desktop\ai-hr-hackaton\ai-hr-hackaton

echo 🛑 Остановка существующих процессов...
taskkill /f /im python.exe >nul 2>&1
taskkill /f /im node.exe >nul 2>&1

echo 🧹 Очистка кэша...
if exist "%PROJECT_ROOT%\backend\api\__pycache__" rmdir /s /q "%PROJECT_ROOT%\backend\api\__pycache__" >nul 2>&1

echo.
echo 🚀 Запуск Backend сервера...
start "AI-HR Backend" cmd /k "cd /d %PROJECT_ROOT%\backend\api && python main_optimized.py"

echo ⏳ Ожидание запуска backend (5 секунд)...
timeout /t 5 /nobreak >nul

echo.
echo 🚀 Запуск Frontend сервера...
start "AI-HR Frontend" cmd /k "cd /d %PROJECT_ROOT%\frontend && set GENERATE_SOURCEMAP=false && set SKIP_PREFLIGHT_CHECK=true && npm start"

echo.
echo ✅ СЕРВЕРЫ ЗАПУСКАЮТСЯ!
echo.
echo 📡 Backend API: http://127.0.0.1:8000
echo 📖 API Документация: http://127.0.0.1:8000/docs
echo 🎯 Monitoring: http://127.0.0.1:8000/api/monitor/google-sheets/status
echo.
echo 🌐 Frontend: http://localhost:3000
echo.
echo 🔥 Система готова к работе!
echo.

timeout /t 10

REM Открываем браузер
start http://localhost:3000

echo Нажмите любую клавишу для выхода...
pause >nul
