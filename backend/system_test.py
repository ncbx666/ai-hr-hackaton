#!/usr/bin/env python3
"""
Комплексный тест AI-HR системы
Проверяет работу всех ключевых компонентов
"""
import os
import sys
import json
from pathlib import Path
from dotenv import load_dotenv

# Загружаем переменные окружения
load_dotenv()

def test_speech_service():
    """Тест речевого сервиса"""
    print("\n🎤 Тестирование SpeechService...")
    try:
        sys.path.append('api')
        from speech_service import SpeechService, MLQuestionGenerator
        
        # Тест инициализации
        service = SpeechService()
        print("✅ SpeechService инициализирован")
        
        # Тест ML генератора вопросов
        ml_gen = MLQuestionGenerator()
        print("✅ MLQuestionGenerator инициализирован")
        
        return True
    except Exception as e:
        print(f"❌ Ошибка SpeechService: {e}")
        return False

def test_ds3_scoring():
    """Тест модуля оценки кандидатов DS3"""
    print("\n📊 Тестирование DS3 модуля...")
    try:
        sys.path.append('../ds3')
        from score_candidate import ScoringModelGemini
        
        # Создаем тестовые данные
        prompts = {
            'scoring': 'Оцени навык {{skill_being_assessed}} на основе вопроса "{{question_text}}" и ответа "{{candidate_answer}}"',
            'experience': 'Оцени опыт на основе вакансии {{vacancy_info}} и резюме {{resume_info}} и ответа {{candidate_answer}}'
        }
        weights = {'hard_skills': 0.4, 'experience': 0.4, 'soft_skills': 0.2}
        
        # Инициализация модели
        model = ScoringModelGemini(prompts, weights)
        print("✅ DS3 ScoringModelGemini инициализирован")
        
        return True
    except Exception as e:
        print(f"❌ Ошибка DS3: {e}")
        return False

def test_google_api():
    """Тест Google Generative AI API"""
    print("\n🤖 Тестирование Google Generative AI API...")
    try:
        import google.generativeai as genai
        
        api_key = os.getenv('GOOGLE_API_KEY')
        if not api_key or api_key == 'your-google-cloud-api-key-here':
            print("❌ Google API ключ не настроен")
            return False
            
        genai.configure(api_key=api_key)
        
        # Простой тест генерации
        model = genai.GenerativeModel('gemini-1.5-pro-latest')
        response = model.generate_content('Привет! Это тест интеграции.')
        
        print("✅ Google Generative AI работает")
        print(f"📝 Тестовый ответ: {response.text[:100]}...")
        
        return True
    except Exception as e:
        print(f"❌ Ошибка Google API: {e}")
        return False

def test_environment():
    """Тест переменных окружения"""
    print("\n🔧 Проверка переменных окружения...")
    
    required_vars = ['GOOGLE_API_KEY', 'DATABASE_URL']
    optional_vars = ['GEMINI_API_KEY', 'OPENAI_API_KEY']
    
    missing_required = []
    for var in required_vars:
        value = os.getenv(var)
        if not value or value.startswith('your-'):
            missing_required.append(var)
        else:
            print(f"✅ {var}: настроен")
    
    for var in optional_vars:
        value = os.getenv(var)
        if value and not value.startswith('your-'):
            print(f"✅ {var}: настроен (опционально)")
        else:
            print(f"⚠️  {var}: не настроен (опционально)")
    
    if missing_required:
        print(f"❌ Не настроены обязательные переменные: {missing_required}")
        return False
    
    return True

def main():
    """Основная функция тестирования"""
    print("🚀 Запуск комплексного теста AI-HR системы")
    print("=" * 50)
    
    tests = [
        ("Переменные окружения", test_environment),
        ("Google API", test_google_api),
        ("SpeechService", test_speech_service),
        ("DS3 Scoring", test_ds3_scoring),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        try:
            if test_func():
                passed += 1
        except Exception as e:
            print(f"❌ Критическая ошибка в тесте '{test_name}': {e}")
    
    print("\n" + "=" * 50)
    print(f"📊 Результаты тестирования: {passed}/{total} тестов пройдено")
    
    if passed == total:
        print("🎉 Все тесты прошли успешно! Система готова к работе.")
        return True
    else:
        print("⚠️  Некоторые тесты не прошли. Проверьте конфигурацию.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
