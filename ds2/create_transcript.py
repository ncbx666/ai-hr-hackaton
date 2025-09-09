# -*- coding: utf-8 -*-
import json
import uuid
from pathlib import Path
import numpy as np
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

# Словарь софт-скиллов
soft_skills = [
    # Общие навыки общения и взаимодействия
    "коммуникация", "работа в команде", "лидерство", "эмпатия",
    "переговоры", "убеждение", "умение слушать", "умение задавать вопросы",
    "conflict management", "negotiation", "persuasion", "active listening",

    # Личностные качества
    "организованность", "ответственность", "гибкость", "креативность",
    "инициативность", "самообучение", "саморазвитие", "стрессоустойчивость",
    "тайм-менеджмент", "мотивация", "адаптация",
    "initiative", "self-learning", "self-development", "stress resistance",
    "time management", "motivation", "adaptability",

    # Решение проблем и критическое мышление
    "критическое мышление", "решение проблем", "анализ", "стратегическое мышление",
    "логическое мышление", "принятие решений",
    "problem solving", "analytical thinking", "strategic thinking",
    "decision making", "critical thinking", "logical thinking",

    # Управление и координация
    "управление временем", "управление проектами", "организация процессов",
    "планирование", "делегирование", "координация",
    "project management", "planning", "coordination", "delegation"
]

# Загружаем модель эмбеддингов (одна модель понимает и русский, и английский)
model = SentenceTransformer("paraphrase-multilingual-MiniLM-L12-v2")
# Предварительно считаем эмбеддинги для словаря
soft_embeddings = model.encode(soft_skills, normalize_embeddings=True)

def classify_text(text, threshold=0.5):
    """Классифицируем текст как soft/hard skill"""
    text_emb = model.encode([text], normalize_embeddings=True)
    sims = cosine_similarity(text_emb, soft_embeddings)[0]
    max_sim = np.max(sims)
    if max_sim >= threshold:
        return "soft_skill", soft_skills[np.argmax(sims)], float(max_sim)
    else:
        return "hard_skill", None, float(max_sim)

# ---------------------------
# Основная функция для проекта
def classify_answer(question: str, answer: str) -> str:
    text = f"Вопрос: {question}\nОтвет: {answer}"
    label, _, _ = classify_text(text)
    return label

# ---------------------------
# Функция сохранения транскрипта
# ---------------------------
# Функция сохранения транскрипта
def generate_transcript(
    candidate_name: str,
    vacancy_info: dict,
    resume_info: dict,
    question: str,
    answer: str,
    assessment_category: str,
    output_path: str = "transcript_output.json"
):
    resume_info_clean = dict(resume_info)
    resume_info_clean.pop("work_experience_summary", None)
    vacancy_info_clean = dict(vacancy_info)
    vacancy_info_clean.pop("key_duties_and_skills", None)
    transcript = {
        "interview_id": str(uuid.uuid4()),
        "candidate_name": candidate_name,
        "vacancy_info": vacancy_info_clean,
        "resume_info": resume_info_clean,
        "dialogue_parts": [
            {
                "question": question,
                "answer": answer,
                "assessment_category": assessment_category
            }
        ]
    }
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(transcript, f, ensure_ascii=False, indent=2)
    print(f"Transcript saved to {output_path}")

# ---------------------------
# main
# ---------------------------
if __name__ == "__main__":
    input_path = "mocks/ds2/input_for_transcript.json"
    output_path = "mocks/ds2/transcript_output.json"

    with open(input_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    candidate_name = data.get("candidate_name", "")
    vacancy_info = data.get("vacancy_info", {})
    resume_info = data.get("resume_info", {})

    # Собираем все вопросы и ответы в списки
    questions = []
    answers = []
    texts = []
    for i in range(1, 100):
        q_key = "question" if i == 1 else f"question_{i}"
        a_key = "answer" if i == 1 else f"answer_{i}"
        if q_key in data and a_key in data:
            question = data[q_key]
            answer = data[a_key]
            questions.append(question)
            answers.append(answer)
            texts.append(f"Вопрос: {question}\nОтвет: {answer}")
        else:
            break

    # Пакетное получение эмбеддингов и классификация
    if texts:
        text_embs = model.encode(texts, normalize_embeddings=True)
        sims = cosine_similarity(text_embs, soft_embeddings)
        max_sims = np.max(sims, axis=1)
        argmax_sims = np.argmax(sims, axis=1)
        assessment_categories = [
            "soft_skill" if max_sim >= 0.5 else "hard_skill"
            for max_sim in max_sims
        ]
    else:
        assessment_categories = []

    dialogue_parts = []
    for question, answer, assessment_category in zip(questions, answers, assessment_categories):
        dialogue_parts.append({
            "question": question,
            "answer": answer,
            "assessment_category": assessment_category
        })

    resume_info_clean = dict(resume_info)
    resume_info_clean.pop("work_experience_summary", None)
    vacancy_info_clean = dict(vacancy_info)
    vacancy_info_clean.pop("key_duties_and_skills", None)
    transcript = {
        "interview_id": data.get("interview_id", str(uuid.uuid4())),
        "candidate_name": candidate_name,
        "vacancy_info": vacancy_info_clean,
        "resume_info": resume_info_clean,
        "dialogue_parts": dialogue_parts
    }
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(transcript, f, ensure_ascii=False, indent=2)
    print(f"Transcript saved to {output_path}")
