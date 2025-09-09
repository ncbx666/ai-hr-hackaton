# Заглушка для интеграции с моделями ML
def generate_question(interview_context: dict) -> str:
    """
    Генерирует следующий вопрос для интервью на основе контекста
    """
    questions = [
        "Расскажите о себе и своем опыте работы.",
        "Какие ваши основные профессиональные навыки?",
        "Опишите сложную задачу, которую вам пришлось решать.",
        "Как вы работаете в команде?",
        "Какие у вас планы на профессиональное развитие?"
    ]
    
    question_number = interview_context.get('question_number', 1)
    if question_number <= len(questions):
        return questions[question_number - 1]
    else:
        return "Спасибо за интервью! У вас есть вопросы к нам?"

def analyze_answer(answer: str, context: dict) -> dict:
    """
    Анализирует ответ кандидата и возвращает оценку
    """
    print(f"[MOCK] ML: Анализ ответа: {answer[:50]}...")
    
    return {
        "score": 0.8,
        "feedback": "Хороший ответ, показывает профессиональные навыки",
        "keywords": ["опыт", "навыки", "команда"],
        "sentiment": "positive"
    }
