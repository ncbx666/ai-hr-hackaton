#!/usr/bin/env python3
"""
Простой WebSocket сервер для интервью без внешних зависимостей
"""

import socket
import threading
import json
import hashlib
import base64
import struct
import time
import random
from datetime import datetime

class SimpleWebSocketServer:
    def __init__(self, host='localhost', port=8001):
        self.host = host
        self.port = port
        self.clients = {}
        
    def websocket_handshake(self, client_socket, headers):
        """Выполняет WebSocket handshake"""
        print("🤝 Начинаем WebSocket handshake")
        print(f"📋 Headers:\n{headers[:500]}...")
        
        key = None
        for line in headers.split('\r\n'):
            if line.lower().startswith('sec-websocket-key'):
                key = line.split(':')[1].strip()
                print(f"🔑 Найден WebSocket ключ: {key}")
                break
        
        if not key:
            print("❌ Sec-WebSocket-Key не найден в заголовках")
            return False
            
        magic_string = "258EAFA5-E914-47DA-95CA-C5AB0DC85B11"
        accept_key = base64.b64encode(
            hashlib.sha1((key + magic_string).encode()).digest()
        ).decode()
        
        print(f"✅ Accept ключ сгенерирован: {accept_key}")
        
        response = (
            "HTTP/1.1 101 Switching Protocols\r\n"
            "Upgrade: websocket\r\n"
            "Connection: Upgrade\r\n"
            f"Sec-WebSocket-Accept: {accept_key}\r\n"
            "\r\n"
        )
        
        try:
            sent_bytes = client_socket.send(response.encode())
            print(f"📤 Handshake ответ отправлен ({sent_bytes} байт)")
            return True
        except Exception as e:
            print(f"❌ Ошибка отправки handshake: {e}")
            return False
    
    def send_websocket_message(self, client_socket, message):
        """Отправляет сообщение через WebSocket"""
        try:
            message_bytes = message.encode('utf-8')
            message_length = len(message_bytes)
            
            if message_length <= 125:
                header = struct.pack('!BB', 0x81, message_length)
            elif message_length <= 65535:
                header = struct.pack('!BBH', 0x81, 126, message_length)
            else:
                header = struct.pack('!BBQ', 0x81, 127, message_length)
            
            sent = client_socket.send(header + message_bytes)
            print(f"📤 Сообщение отправлено ({sent} байт): {message[:100]}...")
            return True
        except Exception as e:
            print(f"❌ Ошибка отправки сообщения: {e}")
            return False
    
    def handle_client(self, client_socket, client_address):
        """Обрабатывает клиента"""
        print(f"🔗 Новое подключение: {client_address}")
        
        try:
            # Читаем HTTP заголовки
            request = client_socket.recv(4096).decode('utf-8')
            print(f"📨 Получен запрос:\n{request[:500]}...")
            
            # Извлекаем session_id из пути
            session_id = "demo-session"
            for line in request.split('\r\n'):
                if line.startswith('GET'):
                    path = line.split()[1]
                    print(f"📍 Путь запроса: {path}")
                    if '/ws/interview/' in path:
                        session_id = path.split('/')[-1]
                    break
            
            # Выполняем handshake
            if not self.websocket_handshake(client_socket, request):
                print("❌ Handshake не удался")
                client_socket.close()
                return
            
            print(f"✅ Handshake успешный")
            self.clients[session_id] = client_socket
            print(f"✅ WebSocket подключение установлено для сессии: {session_id}")
            
            # Отправляем приветственное сообщение
            welcome_msg = json.dumps({
                "type": "welcome",
                "message": f"Добро пожаловать в интервью! Сессия: {session_id}"
            })
            
            if self.send_websocket_message(client_socket, welcome_msg):
                print("📤 Приветственное сообщение отправлено")
            else:
                print("❌ Не удалось отправить приветственное сообщение")
            
            # Симулируем ML вопросы
            self.simulate_interview(client_socket, session_id)
            
        except Exception as e:
            print(f"❌ Ошибка обработки клиента: {e}")
        finally:
            # Закрываем соединение
            try:
                client_socket.close()
            except:
                pass
            
            if session_id in self.clients:
                del self.clients[session_id]
            
            print(f"🔌 Клиент отключился: {session_id}")
    
    def simulate_interview(self, client_socket, session_id):
        """Симулирует процесс интервью"""
        questions = [
            "Расскажите немного о себе и вашем опыте разработки",
            "Какие технологии вы используете в работе?",
            "Как вы решаете сложные технические задачи?",
            "Расскажите о своем последнем проекте",
            "Какие у вас планы на развитие в IT?"
        ]
        
        time.sleep(2)
        
        # Задаем вопросы с интервалом
        for i, question in enumerate(questions):
            if session_id not in self.clients:
                break
                
            question_msg = json.dumps({
                "type": "question",
                "message": question,
                "question_number": i + 1
            })
            
            if self.send_websocket_message(client_socket, question_msg):
                print(f"❓ Вопрос {i+1} отправлен: {question}")
            
            # Симулируем ответ пользователя
            time.sleep(5)
            
            # Отправляем подтверждение получения ответа
            if session_id in self.clients:
                response_msg = json.dumps({
                    "type": "transcript", 
                    "text": "Спасибо за ответ! Переходим к следующему вопросу...",
                    "is_final": True
                })
                self.send_websocket_message(client_socket, response_msg)
            
            time.sleep(2)
        
        # Завершаем интервью
        if session_id in self.clients:
            end_msg = json.dumps({
                "type": "interview_ended",
                "message": "Интервью завершено! Обрабатываем результаты..."
            })
            self.send_websocket_message(client_socket, end_msg)
            
            time.sleep(3)
            
            # Отправляем результаты
            result_msg = json.dumps({
                "type": "processing_completed",
                "message": "Обработка завершена! Результаты готовы.",
                "processing_result": {
                    "status": "completed",
                    "total_score": random.randint(75, 95),
                    "feedback": "Отличное интервью! Хорошие ответы."
                },
                "redirect_to": "/hr/results"
            })
            self.send_websocket_message(client_socket, result_msg)
    
    def start(self):
        """Запускает сервер"""
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server_socket.bind((self.host, self.port))
        server_socket.listen(5)
        
        print(f"🚀 WebSocket сервер запущен на {self.host}:{self.port}")
        print(f"📡 Доступен по адресу: ws://{self.host}:{self.port}/ws/interview/{{session_id}}")
        
        try:
            while True:
                client_socket, client_address = server_socket.accept()
                client_thread = threading.Thread(
                    target=self.handle_client,
                    args=(client_socket, client_address)
                )
                client_thread.daemon = True
                client_thread.start()
        except KeyboardInterrupt:
            print("\n🛑 Сервер остановлен")
        finally:
            server_socket.close()

if __name__ == "__main__":
    server = SimpleWebSocketServer()
    server.start()
