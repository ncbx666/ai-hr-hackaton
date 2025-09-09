#!/usr/bin/env python3
"""
Оптимизированный запуск AI-HR Backend сервера
Минимизирует время загрузки и использует только необходимые компоненты
"""

import os
import sys
import asyncio
import uvicorn
from pathlib import Path

# Оптимизация: устанавливаем переменные окружения для быстрого запуска
os.environ.setdefault("PYTHONUNBUFFERED", "1")
os.environ.setdefault("PYTHONDONTWRITEBYTECODE", "1")  # Не создавать .pyc файлы

def optimize_imports():
    """Предварительная загрузка критически важных модулей"""
    try:
        # Быстрая загрузка основных модулей
        import fastapi
        import pydantic
        import json
        print("✅ Основные модули загружены")
    except ImportError as e:
        print(f"⚠️ Модуль не найден: {e}")

def check_environment():
    """Проверка окружения и оптимизация настроек"""
    print("🔍 Проверка окружения...")
    
    # Проверяем .env файл
    env_file = Path(".env")
    if env_file.exists():
        print("✅ .env файл найден")
    else:
        print("⚠️ .env файл не найден")
    
    # Оптимизация для Windows
    if sys.platform == "win32":
        # Увеличиваем приоритет процесса
        try:
            import psutil
            p = psutil.Process()
            p.nice(psutil.HIGH_PRIORITY_CLASS)
            print("✅ Установлен высокий приоритет процесса")
        except ImportError:
            pass

def main():
    """Главная функция запуска"""
    print("🚀 Запуск оптимизированного AI-HR Backend...")
    
    # Проверка и оптимизация окружения
    check_environment()
    
    # Предварительная загрузка модулей
    optimize_imports()
    
    # Конфигурация Uvicorn для максимальной производительности
    config = {
        "app": "main:app",
        "host": "127.0.0.1",
        "port": 8000,
        "reload": False,  # Отключаем для быстрого запуска
        "access_log": False,  # Отключаем логи доступа
        "loop": "asyncio",
        "workers": 1,
        "log_level": "error",  # Минимальное логирование
        "use_colors": True
    }
    
    print("📡 Сервер будет доступен: http://127.0.0.1:8000")
    print("📖 API документация: http://127.0.0.1:8000/docs")
    print("🎯 Monitoring API: http://127.0.0.1:8000/api/monitor/google-sheets/status")
    
    try:
        # Запуск сервера
        uvicorn.run(**config)
    except KeyboardInterrupt:
        print("\n🛑 Сервер остановлен пользователем")
    except Exception as e:
        print(f"❌ Ошибка запуска сервера: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
