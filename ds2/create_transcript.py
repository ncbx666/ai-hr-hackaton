def classify_question(question: str, vacancy_info: dict) -> str:
    # Ключевые слова для hard skills из вакансии
    hard_keywords = [s.lower() for s in vacancy_info.get("key_duties_and_skills", [])]
    # Универсальные soft skills
    soft_keywords = [
        "команда", "конфликт", "мотивация", "проблема", "решение", "общение",
        "структурное мышление", "стресс", "лидерство", "инициатива", "адаптация"
    ]
    experience_keywords = [
        "опыт", "работа", "должность", "последнее место", "резюме", "стаж", "карьера"
    ]

    q_lower = question.lower()
    if any(word in q_lower for word in experience_keywords):
        return "experience"
    if any(word in q_lower for word in hard_keywords):
        return "hard_skill"
    if any(word in q_lower for word in soft_keywords):
        return "soft_skill"
    return "soft_skill"  # по умолчанию

import json
import uuid
from datetime import datetime
from pathlib import Path
import os

# Попытка импортировать google.generativeai
try:
    import google.generativeai as genai
    GEMINI_API_KEY = os.getenv("GOOGLE_API_KEY")
    if GEMINI_API_KEY:
        genai.configure(api_key=GEMINI_API_KEY)
        GEMINI_MODEL = genai.GenerativeModel('gemini-1.5-flash-latest')
    else:
        GEMINI_MODEL = None
except ImportError:
    GEMINI_MODEL = None

def classify_question_llm(question: str) -> str:
    """
    Классифицирует вопрос с помощью LLM Gemini. Возвращает одну из категорий: hard_skill, soft_skill, experience.
    """
    if not GEMINI_MODEL:
        # Fallback: если нет модели, возвращаем soft_skill
        return "hui"
    prompt = (
        "Определи категорию вопроса для собеседования кандидата. "
        "Варианты: hard_skill, soft_skill, experience.\n"
        "Вопрос: '" + question + "'\n"
        "Ответь только одним словом: hard_skill, soft_skill или experience."
    )
    try:
        response = GEMINI_MODEL.generate_content(prompt)
        category = response.text.strip().lower()
        if "hard" in category:
            return "hard_skill"
        if "soft" in category:
            return "soft_skill"
        if "exp" in category or "опыт" in category:
            return "experience"
        return "soft_skill"
    except Exception as e:
        print(f"LLM classification error: {e}")
        return "soft_skill"

def generate_transcript(
    candidate_name: str,
    vacancy_info: dict,
    resume_info: dict,
    question: str,
    answer: str,
    assessment_category: str,
    skill_assessed: str,
    experience_question_answer: str,
    output_path: str = "transcript_output.json"
):
    transcript = {
        "interview_id": str(uuid.uuid4()),
        "candidate_name": candidate_name,
        "vacancy_info": vacancy_info,
        "resume_info": resume_info,
        "dialogue_parts": [
            {
                "question": question,
                "answer": answer,
                "assessment_category": assessment_category,
                "skill_assessed": skill_assessed
            }
        ],
        "experience_question_answer": experience_question_answer
    }
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(transcript, f, ensure_ascii=False, indent=2)
    print(f"Transcript saved to {output_path}")


if __name__ == "__main__":
    input_path = "mocks/ds2/input_for_transcript.json"
    output_path = "mocks/ds2/transcript_output.json"
    with open(input_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    candidate_name = data["candidate_name"]
    vacancy_info = data["vacancy_info"]
    resume_info = data["resume_info"]

    # Собираем все вопросы и ответы
    dialogue_parts = []
    for i in range(1, 100):
        q_key = "question" if i == 1 else f"question_{i}"
        a_key = "answer" if i == 1 else f"answer_{i}"
        if q_key in data and a_key in data:
            question = data[q_key]
            answer = data[a_key]
            # Используем LLM для классификации
            assessment_category = classify_question_llm(question)
            skill_assessed = ""  # Можно доработать для автозаполнения
            dialogue_parts.append({
                "question": question,
                "answer": answer,
                "assessment_category": assessment_category,
                "skill_assessed": skill_assessed
            })
        else:
            break

    experience_question_answer = ""
    # Можно добавить отдельное поле, если оно есть в data
    if "experience_question_answer" in data:
        experience_question_answer = data["experience_question_answer"]

    transcript = {
        "interview_id": data.get("interview_id", str(uuid.uuid4())),
        "candidate_name": candidate_name,
        "vacancy_info": vacancy_info,
        "resume_info": resume_info,
        "dialogue_parts": dialogue_parts,
        "experience_question_answer": experience_question_answer
    }
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(transcript, f, ensure_ascii=False, indent=2)
    print(f"Transcript saved to {output_path}")
