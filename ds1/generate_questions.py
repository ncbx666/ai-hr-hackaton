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
    # Получаем путь к директории, где находится текущий скрипт
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Формируем абсолютные пути к файлам
    rules_path = os.path.join(script_dir, 'question_template_rules.md')
    prompt_path = os.path.join(script_dir, 'system_prompt.txt')
    
    with open(rules_path, 'r', encoding='utf-8') as f:
        rules = f.read()
    
    with open(prompt_path, 'r', encoding='utf-8') as f:
        system_prompt = f.read()
    
    return rules, system_prompt

def prepare_context(resume_data, vacancy_data):
    """Подготавливает контекст для генерации вопросов."""
    try:
        # Извлекаем ключевые навыки и обязанности из резюме
        resume_responsibilities = resume_data.get('responsibilities', [])
        resume_experience = resume_data.get('experience', [])
        resume_skills = resume_data.get('skills', [])
        
        # Формируем текст из резюме
        resume_parts = []
        if resume_responsibilities:
            if isinstance(resume_responsibilities, list):
                resume_parts.append("Responsibilities: " + "; ".join(resume_responsibilities))
            else:
                resume_parts.append("Responsibilities: " + str(resume_responsibilities))
        
        if resume_experience:
            if isinstance(resume_experience, list):
                exp_texts = []
                for exp in resume_experience:
                    if isinstance(exp, dict):
                        exp_texts.append(f"{exp.get('position', '')} at {exp.get('company', '')}: {exp.get('description', '')}")
                    else:
                        exp_texts.append(str(exp))
                resume_parts.append("Experience: " + "; ".join(exp_texts))
            else:
                resume_parts.append("Experience: " + str(resume_experience))
        
        if resume_skills:
            if isinstance(resume_skills, list):
                resume_parts.append("Skills: " + "; ".join(resume_skills))
            else:
                resume_parts.append("Skills: " + str(resume_skills))
        
        resume_text = " ".join(resume_parts) if resume_parts else "No resume information provided"
        
        # Извлекаем информацию о вакансии
        vacancy_info = vacancy_data.get('vacancy_info', {}) if isinstance(vacancy_data, dict) else {}
        duties = vacancy_info.get('duties', '')
        responsibilities = vacancy_info.get('responsibilities', '')
        requirements = vacancy_info.get('requirements', '')
        skills = vacancy_info.get('skills', '')
        
        # Формируем текст из вакансии
        vacancy_parts = []
        if duties:
            vacancy_parts.append("Duties: " + str(duties))
        if responsibilities:
            vacancy_parts.append("Responsibilities: " + str(responsibilities))
        if requirements:
            vacancy_parts.append("Requirements: " + str(requirements))
        if skills:
            vacancy_parts.append("Skills: " + str(skills))
        
        vacancy_text = " ".join(vacancy_parts) if vacancy_parts else "No job description information provided"
        
        context = {
            'resume_context': resume_text,
            'jd_context': vacancy_text
        }
        
        return context
    except Exception as e:
        print(f"Error preparing context: {e}")
        return {
            'resume_context': 'Error extracting resume information',
            'jd_context': 'Error extracting job description information'
        }

def generate_questions_with_gemini(context, rules, system_prompt, api_key, previous_qa=None, model_name='gemini-1.5-flash'):
    """Генерирует вопросы с помощью Google Gemini API."""
    try:
        # Настраиваем API ключ
        genai.configure(api_key=api_key)
        
        # Создаем модель
        model = genai.GenerativeModel(model_name)
        
        # Формируем полный промпт
        full_prompt = f"""
{system_prompt}

Правила генерации вопросов:
{rules}

Контекст:
Resume: {context['resume_context']}
Job Description: {context['jd_context']}
"""
        
        # Если есть предыдущие вопросы и ответы, добавляем их в промпт
        if previous_qa:
            full_prompt += "\nПредыдущие вопросы и ответы:\n"
            for qa in previous_qa:
                full_prompt += f"Вопрос: {qa.get('question', '')}\n"
                full_prompt += f"Ответ: {qa.get('answer', '')}\n"
                full_prompt += "---\n"
        
        full_prompt += "\nСгенерируй вопросы для интервью в формате JSON массива объектов с полями {action, question, rationale}."

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
    except Exception as e:
        print(f"Error generating questions with Gemini: {e}")
        return [{
            "action": "error",
            "question": "Произошла ошибка при генерации вопросов",
            "rationale": f"Ошибка API: {str(e)}"
        }]

def generate_questions(resume_data, vacancy_data, api_key, previous_qa=None, model_name='gemini-1.5-flash'):
    """Основная функция для генерации вопросов - удобна для интеграции в бэкенд."""
    try:
        rules, system_prompt = load_rules_and_prompt()
        context = prepare_context(resume_data, vacancy_data)
        
        # Генерируем вопросы
        questions = generate_questions_with_gemini(context, rules, system_prompt, api_key, previous_qa, model_name)
        
        return questions
    except Exception as e:
        print(f"Error in generate_questions: {e}")
        return [{
            "action": "error",
            "question": "Произошла ошибка при генерации вопросов",
            "rationale": f"Ошибка: {str(e)}"
        }]

def generate_next_questions(resume_data, vacancy_data, previous_qa, api_key):
    """Генерирует следующие вопросы на основе предыдущих вопросов и ответов."""
    rules, system_prompt = load_rules_and_prompt()
    context = prepare_context(resume_data, vacancy_data)
    
    # Генерируем следующие вопросы
    questions = generate_questions_with_gemini(context, rules, system_prompt, api_key, previous_qa)
    
    return questions

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
