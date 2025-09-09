#!/usr/bin/env python3
"""
Простой HTTP сервер без uvicorn для тестирования
"""

import json
import http.server
import socketserver
from urllib.parse import urlparse, parse_qs
import threading
import time
import random

# Простая эмуляция ML обработки
def simulate_ml_processing(audio_data):
    """Эмулирует ML обработку аудио"""
    time.sleep(2)  # Имитация обработки
    
    # Генерируем случайный вопрос
    questions = [
        "Расскажите о вашем опыте работы с Python",
        "Как вы решаете сложные технические задачи?", 
        "Какой ваш любимый фреймворк и почему?",
        "Опишите свой подход к отладке кода",
        "Как вы изучаете новые технологии?"
    ]
    
    return {
        "status": "processed",
        "question": random.choice(questions),
        "confidence": round(random.uniform(0.7, 0.95), 2),
        "transcript": "Эмуляция распознанного текста...",
        "analysis": {
            "technical_level": random.randint(6, 10),
            "communication": random.randint(7, 10),
            "confidence": random.randint(5, 9)
        }
    }

class AIHRHandler(http.server.BaseHTTPRequestHandler):
    def do_OPTIONS(self):
        """Обработка CORS preflight запросов"""
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()

    def do_GET(self):
        """Обработка GET запросов"""
        parsed_path = urlparse(self.path)
        
        # CORS headers
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        
        if parsed_path.path == '/api/health':
            response = {"status": "OK", "message": "Simple HTTP server is running"}
            self.wfile.write(json.dumps(response).encode())
        elif parsed_path.path == '/api/hr/interviews':
            # Возвращаем массив интервью (не объект с полем interviews)
            response = [
                {
                    "id": "demo-interview-1",
                    "candidateName": "Тестовый Кандидат",
                    "position": "Frontend Developer",
                    "status": "completed",
                    "createdAt": "2025-09-09",
                    "score": 85
                },
                {
                    "id": "demo-interview-2", 
                    "candidateName": "Другой Кандидат",
                    "position": "Backend Developer",
                    "status": "in_progress",
                    "createdAt": "2025-09-09"
                }
            ]
            self.wfile.write(json.dumps(response).encode())
        elif parsed_path.path.startswith('/ws/interview/'):
            # WebSocket эмуляция для интервью
            session_id = parsed_path.path.split('/')[-1]
            
            # Отправляем имитацию WebSocket ответа
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            
            # Эмулируем ML обработку
            ml_result = simulate_ml_processing("audio_data")
            
            response = {
                "type": "question",
                "message": ml_result["question"],
                "question_number": 1,
                "ml_analysis": ml_result["analysis"]
            }
            self.wfile.write(json.dumps(response).encode())
            print(f"🤖 ML Processing for session {session_id}: {ml_result['question']}")
        elif parsed_path.path.startswith('/api/hr/results/'):
            # Результаты интервью
            interview_id = parsed_path.path.split('/')[-1]
            response = {
                "interview_id": interview_id,
                "candidate_name": "Тестовый Кандидат",
                "position": "Frontend Developer", 
                "total_score": 85,
                "details": {
                    "technical_skills": 90,
                    "communication": 80,
                    "problem_solving": 85
                },
                "feedback": "Хорошие технические навыки, отличная коммуникация",
                "status": "completed",
                "google_sheets_url": "https://docs.google.com/spreadsheets/d/demo123/edit"
            }
            self.wfile.write(json.dumps(response).encode())
        else:
            self.send_response(404)
            response = {"error": "Not found"}
            self.wfile.write(json.dumps(response).encode())

    def do_POST(self):
        """Обработка POST запросов"""
        parsed_path = urlparse(self.path)
        
        # Читаем данные запроса
        content_length = int(self.headers.get('Content-Length', 0))
        post_data = b''
        if content_length > 0:
            post_data = self.rfile.read(content_length)
        
        # CORS headers
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        
        if parsed_path.path == '/api/hr/interviews':
            # Создание интервью
            try:
                data = json.loads(post_data.decode('utf-8')) if post_data else {}
            except:
                data = {}
            
            response = {
                "id": "simple-interview-123",
                "status": "created",
                "message": "Interview created successfully via simple HTTP server",
                "data": data,
                "google_sheets_url": "https://docs.google.com/spreadsheets/d/demo123/edit"
            }
            self.wfile.write(json.dumps(response).encode())
            print(f"✅ Interview created: {data.get('title', 'Untitled')}")
            
        elif parsed_path.path == '/api/hr/upload-multi':
            response = {
                "status": "OK",
                "message": "Files uploaded successfully",
                "files": []
            }
            self.wfile.write(json.dumps(response).encode())
            print("📁 Files uploaded")
            
        else:
            self.send_response(404)
            response = {"error": "Not found"}
            self.wfile.write(json.dumps(response).encode())

    def log_message(self, format, *args):
        """Логирование запросов"""
        print(f"[{self.address_string()}] {format % args}")

if __name__ == "__main__":
    PORT = 8000
    HOST = "127.0.0.1"
    
    print(f"🌐 Запуск простого HTTP сервера...")
    print(f"📡 API доступно: http://{HOST}:{PORT}")
    print(f"🔗 Health check: http://{HOST}:{PORT}/api/health")
    print(f"💼 Create interview: POST http://{HOST}:{PORT}/api/hr/interviews")
    
    with socketserver.TCPServer((HOST, PORT), AIHRHandler) as httpd:
        print(f"✅ Сервер запущен на {HOST}:{PORT}")
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\n🛑 Сервер остановлен")
