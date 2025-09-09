import os
import json
from pathlib import Path
import google.generativeai as genai

try:
    GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY')
    genai.configure(api_key=GOOGLE_API_KEY)
except (TypeError, ValueError) as e:
    print(f"ОШИБКА: API-ключ не найден или некорректен. Убедитесь, что вы создали переменную окружения GOOGLE_API_KEY. Ошибка: {e}")
    exit()

class ScoringModelGemini:
    def __init__(self, prompts: dict, weights: dict):
        if not prompts.get("scoring") or not prompts.get("experience"):
            raise ValueError("Словарь prompts должен содержать ключи 'scoring' и 'experience'")
        self.prompts = prompts
        self.weights = weights
        self.model = genai.GenerativeModel(
            'gemini-1.5-pro-latest',
            generation_config={"temperature": 0, "top_p": 0.1}
        )

    def _get_gemini_assessment(self, prompt: str, skill_name: str) -> dict:
        response = None
        try:
            response = self.model.generate_content(prompt)
            json_response_text = response.text.strip().replace("```json", "").replace("```", "")
            return json.loads(json_response_text)
        except Exception as e:
            print(f"!!! Ошибка при обращении к Gemini API или парсинге JSON: {e}")
            if response:
                print(f"!!! Ответ от Gemini, который не удалось распарсить: {response.text}")
            return {"skill_assessed": skill_name, "score": 0, "assessment_comment": f"Ошибка оценки: {e}"}

    def _score_skills(self, transcript_data: dict) -> tuple[float, float, list, list]:
        assessments = {"hard_skill": [], "soft_skill": []}
        dialogue_parts = transcript_data.get("dialogue_parts", [])

        for part in dialogue_parts:
            category = part.get("assessment_category")
            if category in assessments:
                skill_assessed = part.get("skill_assessed", "unknown")
                print(f"-> Оцениваю навык: {skill_assessed}...")
                
                # Используем ручную замену вместо .format()
                prompt = self.prompts["scoring"].replace("{{question_text}}", part.get("question", ""))
                prompt = prompt.replace("{{candidate_answer}}", part.get("answer", ""))
                prompt = prompt.replace("{{skill_being_assessed}}", skill_assessed)

                gemini_result = self._get_gemini_assessment(prompt, skill_name=skill_assessed)
                assessments[category].append(gemini_result)
        
        hard_scores = [res.get("score", 0) for res in assessments["hard_skill"]]
        hard_score_percent = (sum(hard_scores) / (len(hard_scores) * 5)) * 100 if hard_scores else 0
        
        soft_scores = [res.get("score", 0) for res in assessments["soft_skill"]]
        soft_score_percent = (sum(soft_scores) / (len(soft_scores) * 5)) * 100 if soft_scores else 0
        
        return hard_score_percent, soft_score_percent, assessments["hard_skill"], assessments["soft_skill"]

    def _score_experience(self, transcript_data: dict) -> tuple[float, dict]:
        print("-> Оцениваю опыт кандидата...")
        
        # Используем ручную замену вместо .format()
        prompt = self.prompts["experience"].replace("{{vacancy_info}}", json.dumps(transcript_data.get("vacancy_info", {}), ensure_ascii=False))
        prompt = prompt.replace("{{resume_info}}", json.dumps(transcript_data.get("resume_info", {}), ensure_ascii=False))
        prompt = prompt.replace("{{candidate_answer}}", transcript_data.get("experience_question_answer", "Кандидат не предоставил развернутого ответа об опыте."))
        
        gemini_result = self._get_gemini_assessment(prompt, skill_name="Experience")
        
        scores = gemini_result.get("scores", {})
        avg_score_5 = sum(scores.values()) / len(scores) if scores else 0
        
        if gemini_result.get("contradiction_flag", False):
            avg_score_5 *= 0.7

        final_percentage = (avg_score_5 / 5) * 100
        return final_percentage, gemini_result

    def score(self, transcript_data: dict) -> dict:
        hard_score_percent, soft_score_percent, hard_details, soft_details = self._score_skills(transcript_data)
        experience_score_percent, experience_details = self._score_experience(transcript_data)
        
        final_score = (hard_score_percent * self.weights['hard_skills'] +
                       experience_score_percent * self.weights['experience'] +
                       soft_score_percent * self.weights['soft_skills'])

        if final_score >= 75: verdict = "Рекомендован к следующему этапу"
        elif final_score >= 50: verdict = "Требуется дополнительное рассмотрение"
        else: verdict = "Не рекомендован"

        report = {
            "candidate_name": transcript_data.get("candidate_name", "Не указано"),
            "final_score_percent": round(final_score, 2),
            "verdict": verdict,
            "breakdown": {
                "hard_skills": {"score_percent": round(hard_score_percent, 2), "details": hard_details},
                "soft_skills": {"score_percent": round(soft_score_percent, 2), "details": soft_details},
                "experience": {"score_percent": round(experience_score_percent, 2), "details": experience_details}
            }
        }
        return report

if __name__ == "__main__":
    base_path = Path(__file__).resolve().parent.parent
    transcript_path = base_path / "mocks" / "ds2" / "transcript_output.json"
    prompt_path = base_path / "ds3" / "scoring_prompt.md"
    exp_prompt_path = base_path / "ds3" / "experience_prompt.md"
    
    try:
        with open(transcript_path, 'r', encoding='utf-8') as f:
            mock_transcript_data = json.load(f)
        with open(prompt_path, 'r', encoding='utf-8') as f:
            scoring_prompt_template = f.read()
        with open(exp_prompt_path, 'r', encoding='utf-8') as f:
            experience_prompt_template = f.read()
    except FileNotFoundError as e:
        print(f"Ошибка: Не найден файл: {e.filename}")
        exit()

    mock_weights = {"hard_skills": 0.5, "experience": 0.3, "soft_skills": 0.2}
    prompts = {"scoring": scoring_prompt_template, "experience": experience_prompt_template}
    
    print("--- Запуск скоринга кандидата с помощью Gemini ---")
    scorer = ScoringModelGemini(prompts=prompts, weights=mock_weights)
    # Проверяем наличие ключей resume_info и vacancy_info
    if not mock_transcript_data.get("resume_info") or not mock_transcript_data.get("vacancy_info"):
        print("Ошибка: Входные данные должны содержать resume_info и vacancy_info, соответствующие текущим парсерам.")
        exit()
    final_report = scorer.score(transcript_data=mock_transcript_data)

    print("\n--- Итоговый отчет ---")
    print(json.dumps(final_report, indent=2, ensure_ascii=False))

    output_path = base_path / "mocks" / "ds3" / "score_sample.json"
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(final_report, f, indent=2, ensure_ascii=False)
    print(f"\nОтчет сохранен в: {output_path}")
