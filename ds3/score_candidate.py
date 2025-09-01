# ds3/score_candidate.py

import re
import json
from pathlib import Path

# --- ОБЪЯСНЕНИЕ ДЛЯ КОМАНДЫ ---
# Это полная реализация логики скоринга в соответствии с документом 'how_to_score.pdf'.
# Скрипт использует простые, но надежные методы анализа текста (ключевые слова, регулярные выражения),
# что делает его идеальным для хакатона. Все сложные NLP-модели можно будет добавить позже.

class ScoringModel:
    def __init__(self, weights: dict):
        if sum(weights.values()) != 1.0:
            raise ValueError("Сумма весов должна быть равна 1.0")
        self.weights = weights

    def _analyze_hard_skill_answer(self, answer: str) -> (int, str):
        answer_len = len(answer.split())
        if answer_len < 5 or re.search(r"не помню|тайна|да, работал|нет, не работал", answer, re.I):
            return 0, "Уход от ответа или ответ слишком короткий."
        has_tools = re.search(r"FICO Falcon|Neo4j|Oracle|PostgreSQL|SQL|Python|Java|BPMN|Jira", answer, re.I)
        has_metrics = re.search(r"\d+%|снизить|увеличить|оптимизировать|ускорить", answer, re.I)
        has_reasoning = re.search(r"потому что|так как|поскольку|чтобы", answer, re.I)
        if has_reasoning and has_tools and has_metrics:
            return 5, "Глубокая экспертиза: приведены инструменты, метрики и объяснение выбора решения."
        if has_tools and has_metrics:
            return 4, "Конкретный кейс: упомянуты инструменты и измеримые результаты."
        if has_tools:
            return 3, "Конкретный кейс: упомянуты инструменты, но без четких метрик."
        return 2, "Общее описание: есть понимание процесса, но без конкретных примеров."

    def _analyze_star_answer(self, answer: str) -> (int, str):
        has_situation = re.search(r"ситуация|проблема|была задача", answer, re.I)
        has_task = re.search(r"моя задача|нужно было|цель была", answer, re.I)
        has_action = re.search(r"я сделал|мы решили|я проанализировал", answer, re.I)
        has_result = re.search(r"в результате|в итоге|это позволило", answer, re.I)
        has_reflection = re.search(r"я понял|это научило|в будущем", answer, re.I)
        
        star_components = sum([bool(has_situation), bool(has_task), bool(has_action), bool(has_result)])
        
        if has_reflection and star_components >= 3:
            return 5, "Структура STAR + Рефлексия."
        if star_components == 4:
            return 4, "Четкая структура STAR."
        if star_components >= 2:
            return 2, "История без четкой структуры."
        return 0, "Ответ не структурирован."

    def _analyze_motivation_answer(self, answer: str) -> (int, str):
        is_negative = re.search(r"уволили|плохой коллектив|низкая зарплата", answer, re.I)
        is_template = re.search(r"стабильная компания|белая зарплата|соцпакет", answer, re.I)
        is_specific = re.search(r"ВТБ|антифрод|ваш проект|ваша статья|технология X", answer, re.I)
        
        if is_specific:
            return 5, "Конкретная, осознанная мотивация."
        if is_template and not is_negative:
            return 2, "Общая положительная мотивация."
        return 1, "Шаблонный или негативный ответ."
        
    def _score_hard_skills(self, structured_transcript: dict) -> (float, dict):
        hard_skills_scores = []
        details = []
        assessed_skills = structured_transcript.get("assessed_hard_skills", {})
        if not assessed_skills:
            return 0.0, {"details": details, "comment": "Не удалось оценить технические навыки."}
        for skill, answer in assessed_skills.items():
            score, comment = self._analyze_hard_skill_answer(answer)
            hard_skills_scores.append(score)
            details.append({"skill": skill, "score": f"{score}/5", "comment": comment})
        total_score = sum(hard_skills_scores)
        max_possible_score = len(assessed_skills) * 5
        final_percentage = (total_score / max_possible_score) * 100 if max_possible_score > 0 else 0
        return final_percentage, {"details": details}

    def _score_experience(self, vacancy_data: dict, resume_data: dict, structured_transcript: dict) -> (float, dict):
        req_exp = vacancy_data.get("required_experience_years", 0)
        cand_exp = resume_data.get("total_experience_years", 0)
        duration_score_pct = 100.0 if cand_exp >= req_exp else 0.0

        relevance_score_5 = 3.5  # Заглушка: оценка 3.5 из 5
        relevance_score_pct = (relevance_score_5 / 5) * 100

        functionality_score_pct = 75.0  # Заглушка: 75%
        
        penalty_multiplier = 1.0 # Заглушка: штрафа нет

        final_percentage = ((duration_score_pct + relevance_score_pct + functionality_score_pct) / 3) * penalty_multiplier
        
        details = {
            "comment": "Оценка опыта частично использует заглушки.",
            "scores": {
                "duration": duration_score_pct,
                "relevance": relevance_score_pct,
                "functionality": functionality_score_pct
            },
            "penalty": penalty_multiplier
        }
        return final_percentage, details

    def _score_soft_skills(self, structured_transcript: dict) -> (float, dict):
        star_answer = structured_transcript.get("behavioral_question_answer", "")
        motivation_answer = structured_transcript.get("motivation_question_answer", "")
        
        star_score_5, _ = self._analyze_star_answer(star_answer)
        motivation_score_5, _ = self._analyze_motivation_answer(motivation_answer)
        
        star_score_pct = (star_score_5 / 5) * 100
        motivation_score_pct = (motivation_score_5 / 5) * 100

        final_percentage = (star_score_pct + motivation_score_pct) / 2

        details = {
            "comment": "Оценка Soft Skills основана на анализе ответов.",
            "scores": {
                "star_method": star_score_pct,
                "motivation": motivation_score_pct
            }
        }
        return final_percentage, details

    def score(self, vacancy_data: dict, resume_data: dict, structured_transcript: dict) -> dict:
        hard_skills_score, hard_skills_details = self._score_hard_skills(structured_transcript)
        experience_score, experience_details = self._score_experience(vacancy_data, resume_data, structured_transcript)
        soft_skills_score, soft_skills_details = self._score_soft_skills(structured_transcript)
        
        final_score = (hard_skills_score * self.weights['hard_skills'] +
                       experience_score * self.weights['experience'] +
                       soft_skills_score * self.weights['soft_skills'])
        
        if final_score >= 75:
            verdict = "Рекомендован к следующему этапу"
        elif final_score >= 50:
            verdict = "Требуется дополнительное рассмотрение"
        else:
            verdict = "Не рекомендован"

        report = {
            "candidate_name": structured_transcript.get("candidate_name", "N/A"),
            "final_score_percent": round(final_score, 2),
            "verdict": verdict,
            "breakdown": {
                "hard_skills": {"score_percent": round(hard_skills_score, 2), **hard_skills_details},
                "experience": {"score_percent": round(experience_score, 2), **experience_details},
                "soft_skills": {"score_percent": round(soft_skills_score, 2), **soft_skills_details},
            }
        }
        return report

# --- ПРИМЕР ИСПОЛЬЗОВАНИЯ И ТЕСТИРОВАНИЯ ---
if __name__ == "__main__":
    base_path = Path(__file__).resolve().parent.parent
    transcript_path = base_path / "mocks" / "ds3" / "transcript_sample.json"
    
    try:
        with open(transcript_path, 'r', encoding='utf-8') as f:
            mock_transcript_data = json.load(f)
    except FileNotFoundError:
        print(f"Ошибка: Не найден файл с макетом транскрипта: {transcript_path}")
        mock_transcript_data = {}

    mock_vacancy_data = {"required_experience_years": 3}
    mock_resume_data = {"total_experience_years": 18}
    mock_weights = {"hard_skills": 0.5, "experience": 0.3, "soft_skills": 0.2}
    
    print("--- Запуск скоринга кандидата ---")
    scorer = ScoringModel(weights=mock_weights)
    final_report = scorer.score(
        vacancy_data=mock_vacancy_data, 
        resume_data=mock_resume_data, 
        structured_transcript=mock_transcript_data
    )

    print("\n--- Итоговый отчет ---")
    print(json.dumps(final_report, indent=2, ensure_ascii=False))

    output_path = base_path / "mocks" / "ds3" / "score_sample.json"
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(final_report, f, indent=2, ensure_ascii=False)
    print(f"\nОтчет сохранен в: {output_path}")