#!/usr/bin/env python3
import os
from dotenv import load_dotenv
import google.generativeai as genai

# Загружаем переменные окружения
load_dotenv()
api_key = os.getenv('GOOGLE_API_KEY')
print('Testing Google Generative AI...')
print('API Key found:', 'YES' if api_key else 'NO')
print('API Key (first 20 chars):', api_key[:20] + '...' if api_key else 'NONE')

try:
    genai.configure(api_key=api_key)
    
    # Получаем список доступных моделей
    print('\n🔍 Checking available models...')
    models = [m for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
    if models:
        model_name = models[0].name
        print(f'📋 Using model: {model_name}')
        
        model = genai.GenerativeModel(model_name)
        response = model.generate_content('Привет! Это тест работы API. Ответь коротко.')
        print('\n✅ SUCCESS: API работает!')
        print('📝 Ответ от Gemini:', response.text)
    else:
        print('❌ No available models for content generation')
        
except Exception as e:
    print('\n❌ ERROR:', str(e))
    print('🔍 Проверьте правильность API ключа в .env файле')
