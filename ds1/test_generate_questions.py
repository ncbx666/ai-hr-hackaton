#!/usr/bin/env python3
"""
Тестовый скрипт для запуска generate_questions.py с примерами данных
"""

import subprocess
import sys
import os
import json

# Добавляем путь к ds1 в sys.path для импорта модуля
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

def test_command_line_interface():
    """Тестирование через командную строку"""
    print("=== Тестирование через командную строку ===")
    
    # Пути к тестовым файлам
    resume_path = "mocks/ds2/parsed_resume_uglov_vladislav_cv_(7).json"
    vacancy_path = "mocks/ds2/parsed_vacancy_бизнес_аналитик.json"
    output_path = "generated_questions.json"
    
    # Фиктивный API ключ для демонстрации (в реальном использовании нужно заменить на настоящий)
    api_key = "AIzaSyA1e4Rdm1IPPtWUO2q003nnc0S1CUz1Hgw"
    
    # Команда для запуска генерации вопросов
    cmd = [
        "python", "ds1/generate_questions.py",
        resume_path, vacancy_path,
        "--output", output_path,
        "--api_key", api_key
    ]
    
    # Запускаем команду
    result = subprocess.run(cmd, capture_output=True, text=True)
    print("STDOUT:", result.stdout)
    if result.stderr:
        print("STDERR:", result.stderr)
    print("Return code:", result.returncode)

def test_module_interface():
    """Тестирование через импорт модуля"""
    print("\n=== Тестирование через импорт модуля ===")
    
    try:
        # Импортируем модуль
        from ds1.generate_questions import load_resume_and_vacancy, generate_questions
        
        # Пути к тестовым файлам
        resume_path = "mocks/ds2/parsed_resume_uglov_vladislav_cv_(7).json"
        vacancy_path = "mocks/ds2/parsed_vacancy_бизнес_аналитик.json"
        
        # Фиктивный API ключ для демонстрации
        api_key = "AIzaSyA1e4Rdm1IPPtWUO2q003nnc0S1CUz1Hgw"
        
        # Загружаем данные
        resume_data, vacancy_data = load_resume_and_vacancy(resume_path, vacancy_path)
        print("Данные успешно загружены")
        
        # Генерируем вопросы
        questions = generate_questions(resume_data, vacancy_data, api_key)
        print("Вопросы сгенерированы:")
        print(json.dumps(questions, ensure_ascii=False, indent=2))
        
        # Тестирование генерации следующих вопросов
        print("\n=== Тестирование генерации следующих вопросов ===")
        previous_qa = [
            {
                "question": "Расскажите о вашем опыте работы бизнес-аналитиком?",
                "answer": "Я работал бизнес-аналитиком в компании X, где занимался анализом бизнес-процессов и разработкой требований для IT-проектов."
            }
        ]
        
        from ds1.generate_questions import generate_next_questions
        next_questions = generate_next_questions(resume_data, vacancy_data, previous_qa, api_key)
        print("Следующие вопросы сгенерированы:")
        print(json.dumps(next_questions, ensure_ascii=False, indent=2))
        
    except Exception as e:
        print(f"Ошибка при тестировании модуля: {e}")

def main():
    test_command_line_interface()
    test_module_interface()

if __name__ == "__main__":
    main()
