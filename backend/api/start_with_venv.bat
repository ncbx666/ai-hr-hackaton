@echo off
cd /d "C:\Users\79046\Desktop\ai-hr-hackaton"
call .venv\Scripts\activate.bat
cd ai-hr-hackaton\backend\api
echo Starting AI-HR Backend Server with virtual environment...
python simple_server.py
