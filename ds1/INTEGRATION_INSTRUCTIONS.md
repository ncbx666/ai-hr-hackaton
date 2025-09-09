# Инструкция по интеграции модуля генерации вопросов в бэкенд

## Обзор функционала

Модуль `generate_questions.py` предоставляет возможность автоматической генерации вопросов для интервью на основе:
- Резюме кандидата
- Описания вакансии
- Предыдущих вопросов и ответов (для генерации следующих вопросов)

## Установка зависимостей

Убедитесь, что в `requirements.txt` присутствует:
```
google-generativeai==0.1.0
```

Установите зависимости:
```bash
pip install -r requirements.txt
```

## Использование модуля

### Основные функции

1. `generate_questions(resume_data, vacancy_data, api_key, previous_qa=None, model_name='gemini-1.5-flash')`
   - Генерирует вопросы на основе резюме и вакансии
   - `previous_qa` - список предыдущих вопросов и ответов для генерации следующих вопросов
   - `model_name` - название модели Gemini (по умолчанию 'gemini-1.5-flash')

2. `generate_next_questions(resume_data, vacancy_data, previous_qa, api_key)`
   - Генерирует следующие вопросы на основе предыдущих вопросов и ответов

### Пример использования

```python
from ds1.generate_questions import generate_questions, generate_next_questions

# Загрузка данных резюме и вакансии
resume_data = {
    "responsibilities": ["Разработка API", "Анализ требований"],
    "experience": [{"position": "Разработчик", "company": "Компания X", "description": "Разработка веб-приложений"}],
    "skills": ["Python", "FastAPI", "SQL"]
}

vacancy_data = {
    "vacancy_info": {
        "duties": "Разработка и поддержка веб-приложений",
        "responsibilities": "Разработка API, работа с базами данных",
        "requirements": "Опыт работы с Python и веб-фреймворками",
        "skills": ["Python", "FastAPI", "PostgreSQL"]
    }
}

# Генерация начальных вопросов
api_key = "YOUR_GOOGLE_API_KEY"
questions = generate_questions(resume_data, vacancy_data, api_key)

# Генерация следующих вопросов на основе ответов
previous_qa = [
    {
        "question": "Расскажите о вашем опыте работы с Python?",
        "answer": "Я использую Python более 3 лет для разработки веб-приложений."
    }
]
next_questions = generate_next_questions(resume_data, vacancy_data, previous_qa, api_key)
```

## Интеграция в бэкенд

### Замена MockQuestionGenerator

В файле `backend/api/main.py` найдите класс `MockQuestionGenerator` и замените его на реальную реализацию:

```python
import sys
import os
# Добавляем путь к ds1
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from ds1.generate_questions import generate_next_questions

class QuestionGenerator:
    def __init__(self):
        # Получаем API ключ из переменных окружения
        self.api_key = os.getenv("GOOGLE_API_KEY")
        if not self.api_key:
            raise ValueError("GOOGLE_API_KEY не найден в переменных окружения")
    
    async def generate_question(self, transcript: str, question_number: int, job_description: str = "", previous_questions: list = None) -> str:
        try:
            # Подготавливаем данные для генерации
            # В реальной реализации здесь должна быть логика извлечения данных резюме
            # из контекста сессии или базы данных
            resume_data = {
                "responsibilities": [],
                "experience": [],
                "skills": []
            }
            
            vacancy_data = {
                "vacancy_info": {
                    "duties": job_description,
                    "responsibilities": job_description,
                    "requirements": "",
                    "skills": []
                }
            }
            
            # Формируем предыдущие вопросы и ответы
            previous_qa = []
            if previous_questions and len(previous_questions) > 0:
                # Берем последний вопрос как текущий
                previous_qa = [
                    {
                        "question": previous_questions[-1] if previous_questions else "Предыдущий вопрос",
                        "answer": transcript
                    }
                ]
            
            # Генерируем следующие вопросы
            questions = generate_next_questions(resume_data, vacancy_data, previous_qa, self.api_key)
            
            # Возвращаем первый сгенерированный вопрос
            if questions and len(questions) > 0:
                return questions[0].get("question", "Расскажите подробнее о вашем опыте.")
            else:
                return "Расскажите подробнее о вашем опыте."
                
        except Exception as e:
            print(f"[QuestionGenerator] Ошибка генерации вопроса: {e}")
            return "Не удалось сгенерировать вопрос. Расскажите подробнее о своем опыте."
```

### Настройка переменных окружения

Добавьте в файл `.env` в директории `backend`:
```
GOOGLE_API_KEY=ваш_ключ_api_google
```

## Обработка ошибок

Модуль возвращает специальные объекты в случае ошибок:
```python
[
    {
        "action": "error",
        "question": "Произошла ошибка при генерации вопросов",
        "rationale": "Описание ошибки"
    }
]
```

Убедитесь, что ваш код корректно обрабатывает такие случаи.

## Тестирование

Для тестирования используйте скрипт `ds1/test_generate_questions.py`:
```bash
python ds1/test_generate_questions.py
```

## Дополнительные рекомендации

1. Убедитесь, что файлы `ds1/system_prompt.txt` и `ds1/question_template_rules.md` доступны по относительным путям
2. Проверьте, что у API ключа Google есть доступ к Gemini API
3. Для production среды рекомендуется добавить кэширование результатов и ограничение частоты запросов
