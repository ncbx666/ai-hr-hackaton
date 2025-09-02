import google.generativeai as genai
import json

# Установи свой API-ключ
genai.configure(api_key="AIzaSyB7SVJ-31wDSMGqR8RfdbQnnR4DaSQlLP8")

def read_vacancy_text(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        return f.read()

def parse_vacancy_with_gemini(text):
    prompt = (
        "Извлеки из этого текста вакансии структурированные данные в формате JSON. "
        "Верни поля: должность, компания, город, зарплата, требования, обязанности, условия, контакты, ссылка, дата публикации. "
        "Если чего-то нет — оставь пустым.\n\nВакансия:\n" + text
    )
    model = genai.GenerativeModel('gemini-1.5-flash-latest')
    response = model.generate_content(prompt)
    return response.text

if __name__ == "__main__":
    vacancy_path = "vacancy.txt"  # путь к файлу с текстом вакансии
    text = read_vacancy_text(vacancy_path)
    result = parse_vacancy_with_gemini(text)
    # Попробуем преобразовать ответ в JSON, если это возможно
    try:
        data = json.loads(result)
    except Exception:
        data = {"raw_response": result}
    with open("vacancy_structured.json", "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
