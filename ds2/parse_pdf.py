import pdfplumber
import re
import json

def extract_min_experience(text):
    # Ищем диапазон или число лет (например, "1-3 года", "от 2 лет", "3 года")
    match = re.search(r'(?:от\s*)?(\d+)(?:\s*[-–—]\s*(\d+))?\s*год', text, re.IGNORECASE)
    if match:
        return int(match.group(1))
    return 0

def parse_vacancy(text):
    # Название вакансии
    title_match = re.search(r'(?:Вакансия|Должность|Позиция)[:\s]*([\w\s\-]+)', text, re.IGNORECASE)
    title = title_match.group(1).strip() if title_match else ""

    # Опыт работы
    required_experience_years = extract_min_experience(text)

    return {
        "title": title,
        "required_experience_years": required_experience_years
    }

def parse_resume(text):
    # Обязанности (ищем после слова "Обязанности" или "Responsibilities")
    resp_match = re.search(r'(?:Обязанности|Responsibilities)[:\s\-]*([\s\S]+?)(?:\n\s*\n|$)', text)
    responsibilities = []
    if resp_match:
        # Делим по строкам или по дефисам
        responsibilities = [line.strip('–-• ') for line in resp_match.group(1).split('\n') if line.strip()]

    # Общий опыт (ищем диапазоны лет)
    years = re.findall(r'(\d{4})[–—-](\d{4})', text)
    total_experience_years = sum(int(end) - int(start) for start, end in years)

    return {
        "total_experience_years": total_experience_years,
        "responsibilities": responsibilities
    }

def parse_pdf(pdf_path, doc_type):
    text = ""
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"

    if doc_type == 'vacancy':
        return parse_vacancy(text)
    elif doc_type == 'resume':
        return parse_resume(text)
    else:
        return {}

def create_json(vacancy_pdf_path, resume_pdf_path):
    vacancy_info = parse_pdf(vacancy_pdf_path, 'vacancy')
    resume_info = parse_pdf(resume_pdf_path, 'resume')

    output_json = {
        "vacancy_info": vacancy_info,
        "resume_info": resume_info
    }
    return json.dumps(output_json, indent=2, ensure_ascii=False)

# Пример использования:
vacancy_pdf_path = "mocks/ds2/Описание бизнес аналитик.pdf"
resume_pdf_path = "mocks/ds2/Образец резюме 2 Бизнес аналитик.pdf"
final_json = create_json(vacancy_pdf_path, resume_pdf_path)
print(final_json)