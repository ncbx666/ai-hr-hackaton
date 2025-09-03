import google.generativeai as genai
import PyPDF2
import json

# Установи свой API-ключ
genai.configure(api_key="AIzaSyB7SVJ-31wDSMGqR8RfdbQnnR4DaSQlLP8")

def extract_text_from_pdf(pdf_path):
    text = ""
    with open(pdf_path, 'rb') as file:
        reader = PyPDF2.PdfReader(file)
        for page in reader.pages:
            text += page.extract_text() + "\n"
    return text

def parse_resume_with_gemini(text):
    prompt = (
        "Извлеки из этого резюме структурированные данные в формате JSON. "
        "Верни поля: ФИО, email, телефон, навыки, опыт работы, образование, ссылки на соцсети, город, дата рождения. "
        "Если чего-то нет — оставь пустым.\n\nРезюме:\n" + text
    )
    model = genai.GenerativeModel('gemini-1.5-flash-latest')
    response = model.generate_content(prompt)
    return response.text

if __name__ == "__main__":
    pdf_path = "resume.pdf"  # путь к вашему PDF-файлу
    text = extract_text_from_pdf(pdf_path)
    result = parse_resume_with_gemini(text)
    # Попробуем преобразовать ответ в JSON, если это возможно
    try:
        data = json.loads(result)
    except Exception:
        data = {"raw_response": result}
    with open("resume_structured.json", "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)