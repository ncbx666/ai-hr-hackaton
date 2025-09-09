#!/usr/bin/env python3
"""
Тестовый скрипт для запуска generate_questions.py с примерами данных
"""

import subprocess
import sys
import os

def main():
    # Пути к тестовым файлам
    resume_path = "mocks/ds2/parsed_resume_uglov_vladislav_cv_(7).json"
    vacancy_path = "mocks/ds2/parsed_vacancy_бизнес_аналитик.json"
    output_path = "generated_questions.json"
    
    # Фиктивный API ключ для демонстрации (в реальном использовании нужно заменить на настоящий)
    api_key = "YOUR_GOOGLE_API_KEY_HERE"
    
    # Команда для запуска генерации вопросов
    cmd = [
        "python", "ds1/generate_questions.py",
        resume_path, vacancy_path,
        "--output", output_path,
        "--api_key", api_key
    ]
    
    print("Запуск генерации вопросов...")
    print(f"Резюме: {resume_path}")
    print(f"Вакансия: {vacancy_path}")
    print(f"Вывод: {output_path}")
    print(f"Команда: {' '.join(cmd)}")
    print("\nДля реального запуска замените 'YOUR_GOOGLE_API_KEY_HERE' на настоящий API ключ Google Gemini.")
    
    # В реальном сценарии мы бы запустили команду:
    # result = subprocess.run(cmd, capture_output=True, text=True)
    # print(result.stdout)
    # if result.stderr:
    #     print("Ошибки:", result.stderr)

if __name__ == "__main__":
    main()
