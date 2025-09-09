import json
import sys
import os
import google.generativeai as genai

def load_resume_and_vacancy(resume_path, vacancy_path):
    """Загружает данные резюме и вакансии из JSON файлов."""
    with open(resume_path, 'r', encoding='utf-8') as f:
        resume_data = json.load(f)
    
    with open(vacancy_path, 'r', encoding='utf-8') as f:
        vacancy_data = json.load(f)
    
    return resume_data, vacancy_data

def load_rules_and_prompt():
    """Загружает правила и системный промпт."""
    with open('ds1/question_template_rules.md', 'r', encoding='utf-8') as f:
        rules = f.read()
    
    with open('ds1/system_prompt.txt', 'r', encoding='utf-8') as f:
        system_prompt = f.read()
    
    return rules, system_prompt

def prepare_context(resume_data, vacancy_data):
    """Подготавливает контекст для генерации вопросов."""
    # Извлекаем ключевые навыки и обязанности из резюме
    resume_responsibilities = resume_data.get('responsibilities', [])
    resume_text = ' '.join(resume_responsibilities) if isinstance(resume_responsibilities, list) else str(resume_responsibilities)
    
    # Извлекаем информацию о вакансии
    vacancy_info = vacancy_data.get('vacancy_info', {})
    duties = vacancy_info.get('duties', '')
    responsibilities = vacancy_info.get('responsibilities', '')
    vacancy_text = f"{duties} {responsibilities}"
    
    context = {
        'resume_context': resume_text,
        'jd_context': vacancy_text
    }
    
    return context

def generate_questions_with_gemini(context, rules, system_prompt, api_key):
    """Генерирует вопросы с помощью Google Gemini API."""
    # Настраиваем API ключ
    genai.configure(api_key=api_key)
    
    # Создаем модель
    model = genai.GenerativeModel('gemini-2.0-flash-exp')
    
    # Формируем полный промпт
    full_prompt = f"""
{system_prompt}

Правила генерации вопросов:
{rules}

Контекст:
Resume: {context['resume_context']}
Job Description: {context['jd_context']}

Сгенерируй вопросы для интервью в формате JSON массива объектов с полями {{action, question, rationale}}.
"""

    # Генерируем ответ
    response = model.generate_content(full_prompt)
    
    # Парсим JSON с вопросами
    try:
        questions = json.loads(response.text)
        return questions
    except json.JSONDecodeError:
        # Если не удалось распарсить JSON, возвращаем как текст
        return [{
            "action": "ask_general",
            "question": response.text,
            "rationale": "Общий вопрос, сгенерированный моделью"
        }]

def main():
    # Проверяем аргументы командной строки
    if len(sys.argv) < 4:
        print("Usage: python generate_questions.py <resume_json> <vacancy_json> --output <output_json> --api_key <google_api_key>")
        sys.exit(1)
    
    resume_path = sys.argv[1]
    vacancy_path = sys.argv[2]
    
    # Ищем параметры вывода и API ключа
    output_path = 'questions.json'
    api_key = None
    
    for i in range(3, len(sys.argv)):
        if sys.argv[i] == '--output' and i + 1 < len(sys.argv):
            output_path = sys.argv[i + 1]
        elif sys.argv[i] == '--api_key' and i + 1 < len(sys.argv):
            api_key = sys.argv[i + 1]
    
    if not api_key:
        print("Error: Google API key is required. Use --api_key <your_api_key>")
        sys.exit(1)
    
    # Загружаем данные
    resume_data, vacancy_data = load_resume_and_vacancy(resume_path, vacancy_path)
    rules, system_prompt = load_rules_and_prompt()
    context = prepare_context(resume_data, vacancy_data)
    
    # Генерируем вопросы
    questions = generate_questions_with_gemini(context, rules, system_prompt, api_key)
    
    # Сохраняем результат
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(questions, f, ensure_ascii=False, indent=2)
    
    print(f"Questions saved to {output_path}")

if __name__ == "__main__":
    main()
