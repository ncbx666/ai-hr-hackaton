@echo off
REM Combined start script for AI-HR Backend and Frontend
echo 🚀 Starting AI-HR Backend and Frontend...

REM Start backend in a new window
start "AI-HR Backend" /D "%~dp0backend\api" python main_optimized.py

REM Wait a moment for backend to start
timeout /t 3 /nobreak >nul

REM Start frontend in a new window
start "AI-HR Frontend" /D "%~dp0frontend" npm start

echo ⚡ Backend is available at: http://127.0.0.1:8000
echo ⚡ Frontend is available at: http://localhost:3000
echo 📡 Press any key to exit...
pause >nul
