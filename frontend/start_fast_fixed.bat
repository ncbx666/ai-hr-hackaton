@echo off
REM Fixed start script for AI-HR Frontend
echo 🚀 Starting AI-HR Frontend...

REM Change to the correct directory
cd /d "c:\Projects\Python\ai-hr-hackaton\ai-hr-hackaton\frontend"

REM Set environment variables for optimization
set GENERATE_SOURCEMAP=false
set SKIP_PREFLIGHT_CHECK=true
set FAST_REFRESH=false

REM Check if node_modules exists
if not exist node_modules (
    echo 📦 Installing dependencies...
    npm install --silent
)

REM Start the frontend server
echo ⚡ Starting frontend server...
echo 📡 Frontend will be available at: http://localhost:3000
npm start

pause
