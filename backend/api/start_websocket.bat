@echo off
cd /d "C:\Users\79046\Desktop\ai-hr-hackaton"
call .venv\Scripts\activate.bat
cd ai-hr-hackaton\backend\api
echo Starting WebSocket Server for Interview ML Processing...
python simple_websocket_server.py
