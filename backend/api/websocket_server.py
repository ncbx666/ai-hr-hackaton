#!/usr/bin/env python3
"""
WebSocket сервер для интервью с эмуляцией ML обработки
"""

import asyncio
import websockets
import json
import random
import time
import base64
from datetime import datetime

class InterviewWebSocketServer:
    def __init__(self):
        self.connected_clients = {}
        self.interview_sessions = {}
    
    async def simulate_ml_processing(self, audio_data, session_id):
        """Эмулирует ML обработку аудио"""
        print(f"🤖 [ML] Обрабатываю аудио для сессии {session_id}...")
        
        # Имитация времени обработки
        await asyncio.sleep(2)
        
        # Генерируем случайный вопрос
        questions = [
            "Расскажите о вашем опыте работы с Python",
            "Как вы решаете сложные технические задачи?", 
            "Какой ваш любимый фреймворк и почему?",
            "Опишите свой подход к отладке кода",
            "Как вы изучаете новые технологии?",
            "Какие принципы SOLID вы знаете?",
            "Расскажите о работе с базами данных",
            "Как тестируете свой код?"
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
    
    async def handle_client(self, websocket, path):
        """Обработка подключения клиента"""
        session_id = path.split('/')[-1]
        self.connected_clients[session_id] = websocket
        
        print(f"🔗 Клиент подключился к сессии {session_id}")
        
        # Отправляем приветственное сообщение
        await websocket.send(json.dumps({
            "type": "welcome",
            "message": f"Добро пожаловать в интервью! Сессия: {session_id}"
        }))
        
        try:
            async for message in websocket:
                data = json.loads(message)
                await self.process_message(session_id, data, websocket)
                
        except websockets.exceptions.ConnectionClosed:
            print(f"🔌 Клиент отключился от сессии {session_id}")
        finally:
            if session_id in self.connected_clients:
                del self.connected_clients[session_id]
    
    async def process_message(self, session_id, data, websocket):
        """Обработка сообщений от клиента"""
        message_type = data.get('type')
        
        if message_type == 'candidate_info':
            # Получили информацию о кандидате
            name = data.get('name', 'Кандидат')
            self.interview_sessions[session_id] = {
                'name': name,
                'start_time': datetime.now(),
                'questions_asked': 0
            }
            
            await websocket.send(json.dumps({
                "type": "info_received",
                "message": f"Спасибо, {name}! Интервью начинается. Пожалуйста, ответьте на вопросы."
            }))
            
            # Задаем первый вопрос
            await asyncio.sleep(1)
            await websocket.send(json.dumps({
                "type": "question",
                "message": "Расскажите немного о себе и вашем опыте разработки",
                "question_number": 1
            }))
            
        elif message_type == 'audio_chunk':
            # Получили аудио чунк - эмулируем обработку
            audio_data = data.get('data')
            
            # Каждые несколько чанков генерируем транскрипт
            if random.random() < 0.3:  # 30% вероятность
                await websocket.send(json.dumps({
                    "type": "transcript",
                    "text": "Распознанный текст...",
                    "is_final": False
                }))
            
            # Иногда генерируем новый вопрос
            if random.random() < 0.1:  # 10% вероятность
                session = self.interview_sessions.get(session_id, {})
                question_num = session.get('questions_asked', 0) + 1
                
                if question_num < 5:  # Максимум 5 вопросов
                    ml_result = await self.simulate_ml_processing(audio_data, session_id)
                    
                    await websocket.send(json.dumps({
                        "type": "question",
                        "message": ml_result["question"],
                        "question_number": question_num,
                        "ml_analysis": ml_result["analysis"]
                    }))
                    
                    self.interview_sessions[session_id]['questions_asked'] = question_num
        
        elif message_type == 'end_interview':
            # Завершение интервью
            await websocket.send(json.dumps({
                "type": "interview_ended",
                "message": "Интервью завершено! Обрабатываем результаты...",
                "processing": True
            }))
            
            # Эмулируем обработку результатов
            await asyncio.sleep(3)
            
            await websocket.send(json.dumps({
                "type": "processing_completed",
                "message": "Обработка завершена! Результаты готовы.",
                "processing_result": {
                    "status": "completed",
                    "total_score": random.randint(70, 95),
                    "feedback": "Интервью прошло успешно!"
                },
                "redirect_to": "/hr/results"
            }))

if __name__ == "__main__":
    server = InterviewWebSocketServer()
    
    print("🚀 Запуск WebSocket сервера для интервью...")
    print("📡 WebSocket доступен: ws://localhost:8001/ws/interview/{session_id}")
    
    start_server = websockets.serve(
        server.handle_client,
        "localhost", 
        8001,
        subprotocols=["chat"]
    )
    
    print("✅ WebSocket сервер запущен на порту 8001")
    
    asyncio.get_event_loop().run_until_complete(start_server)
    asyncio.get_event_loop().run_forever()
