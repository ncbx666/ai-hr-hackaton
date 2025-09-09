#!/usr/bin/env python3
"""
Flask сервер для AI-HR приложения
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import json

app = Flask(__name__)
CORS(app, origins=["http://localhost:3000", "http://127.0.0.1:3000"])

@app.route('/api/health', methods=['GET'])
def health_check():
    """Проверка работоспособности API"""
    return jsonify({"status": "OK", "message": "Flask AI-HR server is running"})

@app.route('/api/hr/interviews', methods=['POST'])
def create_interview():
    """Создание интервью"""
    try:
        data = request.get_json() or {}
        return jsonify({
            "id": "flask-interview-123",
            "status": "created", 
            "message": "Interview created successfully via Flask",
            "data": data
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/hr/upload-multi', methods=['POST'])
def upload_multi():
    """Загрузка файлов"""
    return jsonify({
        "status": "OK",
        "message": "Files uploaded successfully",
        "files": []
    })

@app.errorhandler(404)
def not_found(error):
    return jsonify({"error": "Not found"}), 404

if __name__ == '__main__':
    print("🌶️ Запуск Flask AI-HR Backend...")
    print("📡 API доступно: http://127.0.0.1:8000")
    print("🔗 Health check: http://127.0.0.1:8000/api/health")
    print("💼 Create interview: POST http://127.0.0.1:8000/api/hr/interviews")
    
    app.run(
        host='127.0.0.1',
        port=8000,
        debug=False,
        threaded=True
    )
