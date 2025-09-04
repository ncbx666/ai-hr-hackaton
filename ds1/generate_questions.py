import json
import sys
from pathlib import Path

# Загружаем JD и/или резюме
if len(sys.argv) < 3:
    print("Usage: python generate_questions.py <jd_json> --output <output_json>")
    sys.exit(1)

jd_path = sys.argv[1]
output_path = sys.argv[3] if len(sys.argv) > 3 and sys.argv[2] == '--output' else 'questions.json'

with open(jd_path, 'r', encoding='utf-8') as f:
    jd_data = json.load(f)

# TODO: Загрузить правила из question_template_rules.md и system_prompt.txt
# Здесь можно реализовать генерацию вопросов по ключевым навыкам, обязанностям и кейсам
questions = []


# Генерация вопросов по ключевым навыкам из JD
skills = jd_data.get('key_duties_and_skills', [])
for skill in skills:
    questions.append({
        "action": "ask_skill",
        "question": f"Расскажите о вашем опыте по теме: {skill}",
        "rationale": "Проверка релевантных навыков кандидата"
    })
    # Follow-up вопрос
    questions.append({
        "action": "follow_up",
        "question": f"Можете привести конкретный пример, где вы применяли навык '{skill}'?",
        "rationale": "Уточнение реального опыта кандидата"
    })

# Генерация вопросов по обязанностям (если есть)
responsibilities = jd_data.get('responsibility', [])
for resp in responsibilities:
    questions.append({
        "action": "ask_case",
        "question": f"Опишите ситуацию, когда вы выполняли задачу: {resp}",
        "rationale": "Проверка опыта выполнения ключевых обязанностей"
    })

# Генерация вопросов по резюме (если есть)
resume = jd_data.get('resume_info', {})
resume_skills = resume.get('skills_from_resume', [])
for skill in resume_skills:
    questions.append({
        "action": "ask_resume_skill",
        "question": f"В вашем резюме указан навык '{skill}'. Как вы его применяли на практике?",
        "rationale": "Проверка заявленных навыков из резюме"
    })

# Ситуационный вопрос
questions.append({
    "action": "ask_case",
    "question": "Опишите ситуацию, когда вам пришлось решать сложную задачу на работе.",
    "rationale": "Оценка проблемного мышления и опыта кандидата"
})

with open(output_path, 'w', encoding='utf-8') as f:
    json.dump(questions, f, ensure_ascii=False, indent=2)

print(f"Questions saved to {output_path}")
