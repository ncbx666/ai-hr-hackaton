# -*- coding: utf-8 -*-
import json
import uuid
import os
from pathlib import Path
import joblib  # pip install joblib
from typing import Optional

# Путь к сохранённой pipeline (поставь сюда файл answer_hard_soft_pipeline.joblib)
MODEL_PATH = Path("models/answer_hard_soft_pipeline.joblib")

# ---------------------------
# Глобальные технические токены (англ/ру) — расширяемый список
# ---------------------------
GLOBAL_HARD_TERMS = {
    "python","sql","pandas","numpy","pytorch","tensorflow","docker","kubernetes","etl","spark","aws","gcp",
    "bigquery","hive","scikit-learn","scikit","xgboost","lightgbm","mlflow","rest api","rest","api","react",
    "nodejs","node","java","c++","matlab","dask","keras","spark","hdfs","hadoop","airflow","mlops","kubeflow",
    "fastapi","flask","tensorflow","pytorch","torch","docker-compose"
}

# Набор точных soft-маркеров — не перебирающийся и узконаправленный, чтобы не ловить технические ответы
DEFAULT_SOFT_KEYWORDS = {
    "команда", "конфликт", "лидерство", "инициатива", "адаптация",
    "teamwork", "communication", "leadership", "initiative", "problem solving",
    "управление временем", "переговор"
}

# ---------------------------
# Rule-based classifier (hard vs soft)
# ---------------------------
class AnswerRuleClassifier:
    """
    Правила для классификации ответа кандидата:
      1) hard_skill — если найден хоть один тех-токен (vacancy + global)
      2) soft_skill — если найден мягкий маркер (но применяется только как fallback)
      Возвращает 'hard_skill' | 'soft_skill' или None.
    """
    def __init__(self, vacancy_info: dict = None):
        vacancy_info = vacancy_info or {}
        try:
            vacancy_terms = [str(s).lower() for s in vacancy_info.get("key_duties_and_skills", []) if s]
        except Exception:
            vacancy_terms = []
        # combine vacancy terms with global tech terms
        self.hard_terms = set(t.lower() for t in GLOBAL_HARD_TERMS) | set(vacancy_terms)
        self.soft_terms = set(t.lower() for t in DEFAULT_SOFT_KEYWORDS)

    def _has_hard_term(self, text: str) -> bool:
        t = text.lower()
        # простой поиск по подстроке: для tech-слов это адекватно (позволяет ловить "rest api", "xgboost", "scikit-learn")
        for ht in self.hard_terms:
            if not ht:
                continue
            if ht in t:
                return True
        return False

    def _has_soft_term(self, text: str) -> bool:
        t = text.lower()
        for st in self.soft_terms:
            if st in t:
                return True
        return False

    def classify(self, text: str) -> Optional[str]:
        if not text:
            return None
        # 1) hard по тех-терминам (приоритет)
        if self._has_hard_term(text):
            return "hard_skill"
        # 2) если нет тех-термов — не делаем вывод soft сразу; даём шанс модели
        # 3) если модель не доступна — можно вернуть soft, но это делается выше в менеджере
        # 4) как последний вариант — если явный soft-маркер есть — вернуть soft
        if self._has_soft_term(text):
            # помечаем как soft только как fallback, менеджер сам решит порядок
            return "soft_skill"
        return None

# ---------------------------
# Singleton loader для локальной pipeline-модели
# ---------------------------
class LocalAnswerPipeline:
    _pipeline = None
    _loaded_path = None

    @classmethod
    def load(cls, path: Path = MODEL_PATH):
        if cls._pipeline is not None and cls._loaded_path == str(path):
            return cls._pipeline
        if path.exists():
            try:
                cls._pipeline = joblib.load(path)
                cls._loaded_path = str(path)
                print(f"[LocalAnswerPipeline] Loaded pipeline from {path}")
            except Exception as e:
                print(f"[LocalAnswerPipeline] Failed to load pipeline from {path}: {e}")
                cls._pipeline = None
        else:
            print(f"[LocalAnswerPipeline] Pipeline not found at {path}")
            cls._pipeline = None
        return cls._pipeline

    @classmethod
    def predict(cls, text: str):
        pipe = cls.load()
        if pipe is None:
            raise RuntimeError("Local pipeline is not loaded")
        return pipe.predict([text])[0]

# ---------------------------
# Менеджер стратегий (singleton)
# ---------------------------
class ClassifierManager:
    def __init__(self, vacancy_info: dict = None, pipeline_path: Path = MODEL_PATH):
        self.rule = AnswerRuleClassifier(vacancy_info)
        self.pipeline_path = pipeline_path
        self.local_available = LocalAnswerPipeline.load(pipeline_path) is not None

    def classify_answer(self, answer_text: str) -> str:
        # 1) Если есть явный hard маркер — вернуть hard незамедлительно
        rule_hard = None
        try:
            rule_pred = self.rule.classify(answer_text)
            if rule_pred == "hard_skill":
                return "hard_skill"
            rule_hard = rule_pred  # возможно 'soft_skill' или None
        except Exception as e:
            print(f"[ClassifierManager] Rule error: {e}")

        # 2) Если локальная модель доступна — доверяем ей (она обучена различать)
        if self.local_available:
            try:
                pred = LocalAnswerPipeline.predict(answer_text)
                if pred in {"hard_skill", "soft_skill"}:
                    return pred
                # если модель вернула что-то странное — продолжим
                return str(pred)
            except Exception as e:
                print(f"[ClassifierManager] Local model error: {e}")

        # 3) Если модель недоступна или не уверена, используем rule soft как fallback
        if rule_hard == "soft_skill":
            return "soft_skill"

        # 4) ultimate fallback
        return "soft_skill"

_GLOBAL_MANAGER: Optional[ClassifierManager] = None

def get_global_manager(vacancy_info: dict = None, pipeline_path: Path = MODEL_PATH) -> ClassifierManager:
    global _GLOBAL_MANAGER
    if _GLOBAL_MANAGER is None:
        _GLOBAL_MANAGER = ClassifierManager(vacancy_info=vacancy_info, pipeline_path=pipeline_path)
    else:
        if vacancy_info is not None:
            _GLOBAL_MANAGER.rule = AnswerRuleClassifier(vacancy_info)
    return _GLOBAL_MANAGER

# Основная функция для проекта: классифицирует ТЕКСТ ОТВЕТА (не вопрос)
def classify_answer(answer_text: str, vacancy_info: dict) -> str:
    manager = get_global_manager(vacancy_info=vacancy_info)
    return manager.classify_answer(answer_text)

# Алиас для совместимости (если где-то зовут classify_question)
def classify_question(question: str, vacancy_info: dict) -> str:
    return classify_answer(question, vacancy_info)
# ---------------------------
# Функция сохранения транскрипта (без изменений логики)
# ---------------------------
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


# ---------------------------
# main — адаптирован: классификация делается по answer (не по question)
# ---------------------------
if __name__ == "__main__":
    input_path = "mocks/ds2/input_for_transcript.json"
    output_path = "mocks/ds2/transcript_output.json"

    # загружаем входной файл
    with open(input_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    candidate_name = data.get("candidate_name", "")
    vacancy_info = data.get("vacancy_info", {})
    resume_info = data.get("resume_info", {})

    # инициализируем менеджер с текущими ключами вакансии
    manager = get_global_manager(vacancy_info=vacancy_info, pipeline_path=MODEL_PATH)

    # Собираем все вопросы и ответы
    dialogue_parts = []
    for i in range(1, 100):
        q_key = "question" if i == 1 else f"question_{i}"
        a_key = "answer" if i == 1 else f"answer_{i}"
        if q_key in data and a_key in data:
            question = data[q_key]
            answer = data[a_key]
            # Классификация теперь по тому, что сказал кандидат (answer)
            assessment_category = classify_answer(answer, vacancy_info)
            skill_assessed = ""  # TODO: автозаполнение навыка можно добавить отдельно
            dialogue_parts.append({
                "question": question,
                "answer": answer,
                "assessment_category": assessment_category,
                "skill_assessed": skill_assessed
            })
        else:
            break

    experience_question_answer = data.get("experience_question_answer", "")

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
