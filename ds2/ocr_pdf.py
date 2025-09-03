# -*- coding: utf-8 -*-
"""
Обновлённый парсер PDF (CPU-only).
Извлекает:
 - vacancy_info (как раньше)
 - resume_info:
    - total_experience_years: total experience (в годах). Если в пределах +-3 месяцев от целого -> округляет до целого.
    - responsibilities: список обязанностей (буллеты) из раздела "Опыт работы" или "Должностные обязанности" / job descriptions.

Обрабатывает все .pdf в /mnt/data и сохраняет результат в /mnt/data/parsed_vacancies_and_resumes.json
"""

from pathlib import Path
import re, json, datetime, math


import pdfplumber

# Пути к вашим файлам
VACANCY_PDF = Path("mocks/ds2/Описание ИТ.pdf")
RESUME_PDF = Path("mocks/ds2/Образец резюме 2 Ведущий специалист ИТ.pdf")

def extract_text_from_pdf(path: Path) -> str:
    text = ""
    with pdfplumber.open(path) as pdf:
        pages = [ (p.extract_text() or "") for p in pdf.pages ]
        text = "\n".join(pages)
    text = re.sub(r'\r\n?', '\n', text)
    text = re.sub(r'\n{3,}', '\n\n', text)
    return text

# Карта месяцев (русские имена, короткие и полные)
MONTHS = {
    'янв':1,'январь':1,'января':1,
    'фев':2,'февраль':2,'февраля':2,
    'мар':3,'март':3,'марта':3,
    'апр':4,'апрель':4,'апреля':4,
    'май':5,'мая':5,
    'июн':6,'июнь':6,'июня':6,
    'июл':7,'июль':7,'июля':7,
    'авг':8,'август':8,'августа':8,
    'сен':9,'сент':9,'сентябрь':9,'сентября':9,
    'окт':10,'октябрь':10,'октября':10,
    'ноя':11,'нояб':11,'ноябрь':11,'ноября':11,
    'дек':12,'декабрь':12,'декабря':12
}

CUR_DATE = datetime.date(2025,9,3)  # согласно системной информации в dev-правилах

# Регулярные шаблоны для дат/диапазонов в резюме
# Примеры поддерживаемых форматов:
# "янв 2018 — апр 2020", "январь 2018 - апрель 2020", "01.2018 - 04.2020", "2018 — 2020", "с 2018 по настоящее время", "2018 - настоящее время"
MONTH_YEAR_RE = r'(?:(\d{1,2})[.\-](\d{4}))'  # 01.2018
TEXT_MONTH_YEAR_RE = r'((?:' + r'|'.join(re.escape(m) for m in MONTHS.keys()) + r')\s*\d{4})'  # 'янв 2018' etc.
YEAR_ONLY_RE = r'(\d{4})'
RANGE_SEP = r'[-–—]|to|по|—|–'
# Собираем несколько вариантов для поиска диапазонов
RANGE_PATTERNS = [
    re.compile(rf'({TEXT_MONTH_YEAR_RE})\s*(?:{RANGE_SEP})\s*(настоящее время|по настоящее время|по тн|по н\.в\.|по нв|{TEXT_MONTH_YEAR_RE}|{YEAR_ONLY_RE})', flags=re.IGNORECASE),
    re.compile(rf'({MONTH_YEAR_RE})\s*(?:{RANGE_SEP})\s*(настоящее время|по настоящее время|{MONTH_YEAR_RE}|{YEAR_ONLY_RE})', flags=re.IGNORECASE),
    re.compile(rf'с\s+({YEAR_ONLY_RE})\s+по\s+(настоящее время|{YEAR_ONLY_RE})', flags=re.IGNORECASE),
    re.compile(rf'({YEAR_ONLY_RE})\s*(?:{RANGE_SEP})\s*(настоящее время|{YEAR_ONLY_RE})', flags=re.IGNORECASE)
]

def parse_month_year_token(token: str):
    token = token.strip().lower()
    # try dd.yyyy or mm.yyyy
    m = re.match(r'(\d{1,2})[.\-](\d{4})', token)
    if m:
        mon = int(m.group(1))
        yr = int(m.group(2))
        return datetime.date(yr, mon, 1)
    # try textual month like 'янв 2018' or 'января 2018'
    m2 = re.search(r'(' + r'|'.join(re.escape(k) for k in MONTHS.keys()) + r')\s*(\d{4})', token)
    if m2:
        monname = m2.group(1)
        yr = int(m2.group(2))
        mon = MONTHS.get(monname[:3], MONTHS.get(monname, 1))
        # ensure mapping by full name
        mon = MONTHS.get(monname, MONTHS.get(monname[:3], mon))
        try:
            return datetime.date(yr, mon, 1)
        except Exception:
            return None
    # try year only
    m3 = re.match(r'(\d{4})', token)
    if m3:
        yr = int(m3.group(1))
        return datetime.date(yr, 1, 1)
    # special tokens
    if re.search(r'настоящее', token):
        return CUR_DATE
    return None

def find_date_ranges(text: str):
    ranges = []
    # search for all patterns
    for pat in RANGE_PATTERNS:
        for m in pat.finditer(text):
            groups = m.groups()
            # flatten non-empty groups to tokens
            tokens = [g for g in groups if g]
            if not tokens:
                continue
            # pick first as start, last as end (heuristic)
            start_tok = tokens[0]
            end_tok = tokens[-1]
            start_dt = parse_month_year_token(start_tok)
            end_dt = parse_month_year_token(end_tok)
            if start_dt and end_dt:
                # normalize end to last day of the month for duration calc
                # but we'll store as date objects for merging
                ranges.append((start_dt, end_dt))
    # additionally, catch formats like "2018–2020" with en-dash without spaces - some may be missed by patterns, but RANGE_PATTERNS cover common cases
    return ranges

def months_between(d1: datetime.date, d2: datetime.date):
    return (d2.year - d1.year) * 12 + (d2.month - d1.month) + (1 if d2.day >= d1.day else 0)  # approximate

def merge_intervals(intervals):
    # intervals: list of (date_start, date_end)
    if not intervals:
        return []
    # sort by start
    intervals_sorted = sorted(intervals, key=lambda x: x[0])
    merged = [intervals_sorted[0]]
    for cur in intervals_sorted[1:]:
        last = merged[-1]
        # if overlap or contiguous (start <= last_end + 1 month) -> merge
        if cur[0] <= last[1] + datetime.timedelta(days=31):
            # new end is max(last.end, cur.end)
            merged[-1] = (last[0], max(last[1], cur[1]))
        else:
            merged.append(cur)
    return merged

# Извлечение обязанностей из блока "Опыт работы"
HEADING_RE = re.compile(r'^\s*(Опыт работы|Работа|Профессиональный опыт|Должность|Опыт)\b', flags=re.IGNORECASE | re.MULTILINE)
SECTION_HEADINGS = [
    r'Обязанности', r'Требования', r'Опыт работы', r'Опыт', r'Профессиональный опыт', r'Навыки', r'Резюме'
]
SECTION_HEADING_RE = re.compile(r'^\s*(?:' + r'|'.join(SECTION_HEADINGS) + r')\b', flags=re.IGNORECASE | re.MULTILINE)

def extract_responsibilities_from_experience_section(text: str):
    # Find the experience section
    m = HEADING_RE.search(text)
    if m:
        start = m.end()
        # find next major heading
        next_h = SECTION_HEADING_RE.search(text, pos=start)
        end = next_h.start() if next_h else len(text)
        exp_block = text[start:end].strip()
    else:
        # fallback: try to find "Опыт работы" anywhere
        m2 = re.search(r'Опыт работы', text, flags=re.IGNORECASE)
        if m2:
            start = m2.end()
            next_h = SECTION_HEADING_RE.search(text, pos=start)
            end = next_h.start() if next_h else len(text)
            exp_block = text[start:end].strip()
        else:
            exp_block = text  # as fallback use entire text (risky)
    # split into lines and group by job blocks using date lines as separators
    lines = [ln.rstrip() for ln in exp_block.splitlines() if ln.strip()!='']
    if not lines:
        return []
    # detect lines that contain date ranges -> split there
    date_line_idx = []
    for i, ln in enumerate(lines):
        if re.search(r'\d{4}', ln) and re.search(r'[-–—]|по|по настоящее', ln):
            date_line_idx.append(i)
        elif re.search(r'\b(настоящее время|по настоящее время|по н\.в\.|по нв)\b', ln, flags=re.IGNORECASE):
            date_line_idx.append(i)
    # If none found, fallback to searching for bullets "- " or "•"
    if not date_line_idx:
        bullets = [ln for ln in lines if re.match(r'^\s*[-•\*]\s+', ln)]
        if bullets:
            # return bullets cleaned
            return [re.sub(r'^\s*[-•\*]\s*', '', b).strip() for b in bullets]
        # else try to find 'Обязанности' inside lines
        for i, ln in enumerate(lines):
            if re.search(r'обязанности', ln, flags=re.IGNORECASE):
                # take subsequent lines as bullets
                res = []
                for j in range(i+1, min(i+20, len(lines))):
                    candidate = lines[j]
                    if candidate.startswith('-') or candidate.startswith('•') or len(candidate.split())>3:
                        res.append(re.sub(r'^[-•\*]\s*', '', candidate).strip())
                if res:
                    return res
        return []
    # Use date_line_idx to partition into job blocks
    blocks = []
    indices = date_line_idx + [len(lines)]
    for idx_i in range(len(indices)-1):
        start_i = indices[idx_i]
        end_i = indices[idx_i+1]
        block_lines = lines[start_i:end_i]
        blocks.append(block_lines)
    # From each block, extract bullets or sentences that look like responsibilities
    responsibilities = []
    for b in blocks:
        # collect lines starting with dash or containing 'Обязанности' or lines after job title
        for ln in b:
            ln_clean = ln.strip()
            if re.match(r'^[-•\*]\s*', ln_clean):
                responsibilities.append(re.sub(r'^[-•\*]\s*', '', ln_clean).strip())
            else:
                # if line long and contains verbs like 'разрабатывать', 'анализировать', 'проводить', 'готовить', 'составлять'
                if re.search(r'\b(разраб|анализ|провод|готов|состав|подгот|администр|настраив|участв|проводит|внедр)\w*', ln_clean, flags=re.IGNORECASE):
                    responsibilities.append(ln_clean)
    # deduplicate and clean
    cleaned = []
    for r in responsibilities:
        r2 = re.sub(r'\s+', ' ', r).strip()
        if r2 and r2 not in cleaned:
            cleaned.append(r2)
    return cleaned

def compute_total_experience_years_from_text(text: str):
    ranges = find_date_ranges(text)
    if not ranges:
        return None, []
    merged = merge_intervals(ranges)
    # compute total months
    total_months = 0
    for s,e in merged:
        # count months inclusive from s to e
        months = (e.year - s.year) * 12 + (e.month - s.month) + 1
        total_months += months
    total_years = total_months / 12.0
    # rounding rule: if within +-3 months (0.25 year) of nearest integer -> round to int
    nearest = round(total_years)
    if abs(total_years - nearest) <= 0.25:
        total_exp = int(nearest)
    else:
        total_exp = round(total_years, 2)
    return total_exp, merged

# Функция парсинга отдельного файла (универсальная: вакансии + резюме)
def parse_file(path: Path):
    text = extract_text_from_pdf(path)
    title = path.stem
    # Более гибкий поиск секций
    def extract_section_by_heading_or_keyword(names):
        for name in names:
            # ищем как заголовок
            pat = re.compile(r'(' + re.escape(name) + r'(?:\s*\(.*?\))?)\s*[:\-\—]*\s*', flags=re.IGNORECASE)
            m = pat.search(text)
            if m:
                start = m.end()
                next_h = re.search(r'^\s*(Обязанности|Требования|Опыт работы|Условия|Описание вакансии)\b', text[start:], flags=re.IGNORECASE | re.MULTILINE)
                if next_h:
                    end = start + next_h.start()
                else:
                    end = len(text)
                snippet = text[start:end].strip()
                snippet = re.sub(r'^\s*[-•\*]\s*', '', snippet, flags=re.MULTILINE)
                snippet = re.sub(r'\n{2,}', '\n', snippet).strip()
                if snippet:
                    return snippet
        # если не найдено как заголовок, ищем по ключевым словам в тексте
        for name in names:
            kw_pat = re.compile(rf'{re.escape(name)}[\s:–—-]*([^\n]{{10,}})', flags=re.IGNORECASE)
            m = kw_pat.search(text)
            if m:
                return m.group(1).strip()
        return ""

    obr = extract_section_by_heading_or_keyword(['Обязанности', 'Должностные обязанности', 'Функциональные обязанности', 'Что делать', 'Основные задачи'])
    treb = extract_section_by_heading_or_keyword(['Требования', 'Квалификация', 'Требуемые навыки', 'Необходимые навыки', 'Требования к кандидату'])

    # Более гибкий поиск опыта работы
    exp_vac = None
    exp_patterns = [
        r'(?:опыт работы|стаж|требуемый опыт|опыт не менее|от)\s*([\d]{1,2})\s*[-–—]?(\d{0,2})?\s*(лет|год|года|месяц|месяцев|месяца)',
        r'([\d]{1,2})\s*[-–—]([\d]{1,2})\s*лет',
        r'([\d]{1,2})\s*лет',
        r'от\s*([\d]{1,2})\s*лет'
    ]
    for pat in exp_patterns:
        exp_search = re.search(pat, text, flags=re.IGNORECASE)
        if exp_search:
            if exp_search.group(1):
                num = int(exp_search.group(1))
                if exp_search.lastindex and exp_search.lastindex >= 3 and exp_search.group(3) and 'месяц' in exp_search.group(3).lower():
                    exp_vac = round(num/12,2)
                else:
                    exp_vac = num
                break

    # resume-specific extraction
    total_exp, merged_intervals = compute_total_experience_years_from_text(text)
    responsibilities = extract_responsibilities_from_experience_section(text)
    return {
        "filename": path.name,
        "vacancy_info": {
            "title": title,
            "required_experience_years": exp_vac,
            "duties": obr if obr is not None else "",
            "requirements": treb if treb is not None else ""
        },
        "resume_info": {
            "total_experience_years": total_exp,
            "responsibilities": responsibilities
        },
        "_debug": {
            "found_date_ranges": [ (s.isoformat(), e.isoformat()) for s,e in find_date_ranges(text) ],
            "merged_intervals": [ (s.isoformat(), e.isoformat()) for s,e in merged_intervals ]
        }
    }



# Парсим только два конкретных файла и сохраняем в отдельные JSON
vacancy_data = parse_file(VACANCY_PDF)
resume_data = parse_file(RESUME_PDF)



# Извлекаем только название вакансии из имени файла (после слова "описание" или "Описание")
import re
vacancy_filename = vacancy_data["filename"]
title_match = re.search(r'[Оо]писание\s*(.*)\.pdf', vacancy_filename)
vacancy_title = title_match.group(1).strip() if title_match else vacancy_filename.replace('.pdf','')

vacancy_json = {
    "filename": vacancy_filename,
    "vacancy_info": {
        "title": vacancy_title,
        "required_experience_years": vacancy_data["vacancy_info"].get("required_experience_years"),
        "duties": vacancy_data["vacancy_info"].get("duties")
    }
}
with open("mocks/ds2/parsed_vacansy.json", "w", encoding="utf-8") as f:
    json.dump(vacancy_json, f, ensure_ascii=False, indent=2)

# Формируем и сохраняем resume
resume_json = {
    "filename": resume_data["filename"],
    "vacancy_info": {
        "title": resume_data["vacancy_info"].get("title"),
        "experience_years": resume_data["vacancy_info"].get("required_experience_years"),
        "duties": resume_data["vacancy_info"].get("duties"),
        "requirements": resume_data["vacancy_info"].get("requirements")
    }
}
with open("mocks/ds2/parsed_resume.json", "w", encoding="utf-8") as f:
    json.dump(resume_json, f, ensure_ascii=False, indent=2)

print("\nSaved JSON to: mocks/ds2/parsed_vacansy.json and mocks/ds2/parsed_resume.json")
