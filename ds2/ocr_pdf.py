from pathlib import Path
import re, json, datetime, math

import pdfplumber

# Пути к папкам
VACANCY_DIR = Path("mocks/ds2/vacansy")
CV_DIR = Path("mocks/ds2/cv")
OUTPUT_DIR = Path("mocks/ds2")

def get_pdf_files(directory: Path) -> list[Path]:
    """Get all PDF files from directory"""
    return list(directory.glob("*.pdf"))

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
    # textual month-year ranges like 'янв 2018 - апр 2020' (allowing whitespace/newlines)
    re.compile(rf'({TEXT_MONTH_YEAR_RE})\s*(?:{RANGE_SEP})\s*(настоящее время|по настоящее время|по тн|по н\.в\.|по нв|{TEXT_MONTH_YEAR_RE}|{YEAR_ONLY_RE})', flags=re.IGNORECASE | re.DOTALL),
    # numeric month.year ranges like '01.2018 - 04.2020'
    re.compile(rf'({MONTH_YEAR_RE})\s*(?:{RANGE_SEP})\s*(настоящее время|по настоящее время|{MONTH_YEAR_RE}|{YEAR_ONLY_RE})', flags=re.IGNORECASE | re.DOTALL),
    # patterns with 'с 2018 по настоящее время' and year ranges; allow newlines between tokens
    re.compile(rf'с\s+({YEAR_ONLY_RE})\s+по\s+(настоящее время|{YEAR_ONLY_RE})', flags=re.IGNORECASE | re.DOTALL),
    re.compile(rf'({YEAR_ONLY_RE})\s*(?:{RANGE_SEP})\s*(настоящее время|{YEAR_ONLY_RE})', flags=re.IGNORECASE | re.DOTALL),
    # loose pattern: year-year even if on different lines like '2010\n—\n2018'
    re.compile(rf'({YEAR_ONLY_RE})\s*(?:{RANGE_SEP})\s*({YEAR_ONLY_RE}|настоящее время)', flags=re.IGNORECASE | re.DOTALL)
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
    # 1) search using the defined patterns (covers many common cases)
    for pat in RANGE_PATTERNS:
        for m in pat.finditer(text):
            groups = m.groups()
            tokens = [g for g in groups if g]
            if not tokens:
                continue
            start_tok = tokens[0]
            end_tok = tokens[-1]
            start_dt = parse_month_year_token(start_tok)
            end_dt = parse_month_year_token(end_tok)
            if start_dt and end_dt:
                ranges.append((start_dt, end_dt))

    # 2) token-scan fallback: find all date-like tokens and pair nearby tokens
    token_regex = re.compile(r'(' + r'|'.join([r'\d{1,2}[.\-]\d{4}'] + [re.escape(k) + r'\s*\d{4}' for k in MONTHS.keys()] + [r'\d{4}']) + r')', flags=re.IGNORECASE)
    tokens = []
    for m in token_regex.finditer(text):
        tok = m.group(0)
        dt = parse_month_year_token(tok)
        if dt:
            tokens.append((m.start(), m.end(), tok, dt))
    # pair neighboring tokens if they are close in the text (<=80 chars)
    for i in range(len(tokens)-1):
        s0, e0, t0, d0 = tokens[i]
        s1, e1, t1, d1 = tokens[i+1]
        if s1 - e0 <= 80:
            # ensure a separator like dash or 'по' exists between them or it's reasonable proximity
            mid = text[e0:s1]
            if re.search(r'[-–—]|по|до|настоящее|по настоящее', mid, flags=re.IGNORECASE) or len(mid.strip()) < 50:
                ranges.append((d0, d1))
        # Also if second token is 'настоящее время' (parsed to CUR_DATE) pair with previous
    # 3) explicit duration phrases like '3 года 9 месяцев' anywhere -> convert to ranges using approximate start
    for m in re.finditer(r'([0-9]{1,2})\s*год(?:а|ов)?(?:\s*([0-9]{1,2})\s*месяц)?', text, flags=re.IGNORECASE):
        yrs = int(m.group(1))
        months = int(m.group(2)) if m.lastindex and m.group(2) else 0
        # represent as a pseudo-range ending at CUR_DATE and starting months ago (approximate)
        total_months = yrs * 12 + months
        if total_months > 0:
            end_dt = CUR_DATE
            start_month = end_dt.month - (total_months - 1)
            start_year = end_dt.year
            # normalize start_month/year
            while start_month <= 0:
                start_month += 12
                start_year -= 1
            start_dt = datetime.date(start_year, start_month, 1)
            ranges.append((start_dt, end_dt))

    # deduplicate ranges
    uniq = []
    for r in ranges:
        if r not in uniq:
            uniq.append(r)
    return uniq

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
        # year-range like '2018 — 2020' or 'янв 2018 — апр 2020'
        if re.search(r'\d{4}', ln) and re.search(r'[-–—]|по|по настоящее', ln):
            date_line_idx.append(i)
        # explicit tokens 'настоящее время'
        elif re.search(r'\b(настоящее время|по настоящее время|по н\.в\.|по нв)\b', ln, flags=re.IGNORECASE):
            date_line_idx.append(i)
        # duration-only like '3 года 9 месяцев' or '11 месяцев'
        elif re.search(r"\b[0-9]{1,2}\s*(год|года|лет|месяц|месяцев|месяца)\b", ln, flags=re.IGNORECASE):
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
        # include previous line as header/context when possible (e.g., job title/company may be above date)
        if start_i > 0:
            start_i = start_i - 1
        end_i = indices[idx_i+1]
        block_lines = lines[start_i:end_i]
        blocks.append(block_lines)
    # From each job-block, collect full responsibility lines (preserve bullets and multi-line descriptions)
    responsibilities = []
    verb_re = re.compile(r'\b(разраб|анализ|провод|готов|состав|подгот|администр|настраив|участв|проводит|внедр|настра|настрой|инстал|админ|обслужив|настройка|конфигурац)\w*', flags=re.IGNORECASE)
    for b in blocks:
        # b is a list of lines belonging to a single job block; keep lines that are not date headers
        cleaned_lines = []
        for ln in b:
            s = ln.strip()
            if not s:
                continue
            # skip obvious date lines or tokens like 'настоящее время'
            if re.search(r'\b(настоящее время|по настоящее время|по н\.в\.|по нв)\b', s, flags=re.IGNORECASE):
                continue
            if re.match(r'^\d{4}\b', s) or re.match(r'^\d{1,2}[\.\-/]\d{4}\b', s):
                continue
            # textual month + year (e.g., 'янв 2018') -> skip
            if re.search(r'(' + r'|'.join(re.escape(k) for k in MONTHS.keys()) + r')\s*\d{4}', s, flags=re.IGNORECASE):
                continue
            cleaned_lines.append(s)

        if not cleaned_lines:
            continue

        # If bullets exist among cleaned_lines, reconstruct bullet items with continuations
        items = []
        i = 0
        while i < len(cleaned_lines):
            line = cleaned_lines[i]
            m = re.match(r'^[-•\*\u2022]\s*(.+)', line)
            if m:
                cur = m.group(1)
                i += 1
                # append continuation lines until next bullet or a likely header/date
                while i < len(cleaned_lines):
                    nxt = cleaned_lines[i]
                    if re.match(r'^[-•\*\u2022]\s*', nxt):
                        break
                    if re.match(r'^\d{4}\b', nxt) or re.match(r'^\d{1,2}[\.\-/]\d{4}\b', nxt):
                        break
                    cur += ' ' + nxt
                    i += 1
                items.append(cur.strip())
            else:
                # accumulate paragraph-like lines
                cur = line
                i += 1
                while i < len(cleaned_lines):
                    nxt = cleaned_lines[i]
                    if re.match(r'^[-•\*\u2022]\s*', nxt):
                        break
                    # If current ends with sentence terminator and next starts with uppercase, treat as new item
                    if cur and cur[-1] in '.!?':
                        if nxt and nxt[0].isupper():
                            break
                    # Otherwise consider it a continuation
                    cur += ' ' + nxt
                    i += 1
                items.append(cur.strip())

        # Filter and accept items: keep reasonable-length items or those containing target verbs
        for it in items:
            if not it:
                continue
            # skip lines that look like headers/locations
            if re.search(r'\b(Москва|Санкт|www\.|http:|https:|г\.|ул\.|тел:|@)\b', it, flags=re.IGNORECASE):
                continue
            if len(it) < 6:
                continue
            # accept if it contains an action verb or is a descriptive phrase
            if verb_re.search(it) or len(it) > 30:
                responsibilities.append(it)

    # fallback: search whole document for explicit 'Обязанности' or 'Должностные обязанности' bullets
    if not responsibilities:
        m = re.search(r'(Обязанности|Должностные обязанности|Функциональные обязанности)[\s\S]{0,800}', text, flags=re.IGNORECASE)
        if m:
            snippet = m.group(0)
            bullets = re.findall(r'[-•\*]\s*(.+)', snippet)
            for b in bullets:
                b2 = b.strip()
                if len(b2) > 6:
                    responsibilities.append(b2)

    # deduplicate and clean; apply merging heuristics to join split fragments
    cleaned = []
    for r in responsibilities:
        r2 = re.sub(r'\s+', ' ', r).strip()
        if not r2:
            continue
        if cleaned and len(cleaned[-1]) < 60 and not re.search(r'[\.!;]$', cleaned[-1]):
            cleaned[-1] = cleaned[-1] + ' ' + r2
        elif r2 not in cleaned:
            cleaned.append(r2)
    # second pass: join items that were split in the middle of a sentence
    merged = []
    i = 0
    while i < len(cleaned):
        cur = cleaned[i]
        if i + 1 < len(cleaned):
            nxt = cleaned[i+1]
            # join if current doesn't end with sentence terminator and next starts with lowercase or is short
            if not re.search(r'[\.!;:]$', cur) and (nxt and (nxt[0].islower() or len(nxt) < 40)):
                cur = cur + ' ' + nxt
                i += 2
                # try to also merge further short fragments
                while i < len(cleaned) and len(cleaned[i]) < 40 and not re.search(r'[\.!;:]$', cur):
                    cur = cur + ' ' + cleaned[i]
                    i += 1
                merged.append(cur.strip())
                continue
        merged.append(cur)
        i += 1
    return merged

def compute_total_experience_years_from_text(text: str):
    # First, prefer an explicit total experience statement like 'Опыт работы — 2 года 4 месяца' or 'Опыт работы — 11 месяцев'
    # Match months-only explicit declaration first
    m_exp_months = re.search(r'Опыт\s+работ[ыи]\s*[:\-–—]?\s*([0-9]{1,2})\s*(?:месяц(?:а|ев)?)', text, flags=re.IGNORECASE)
    if m_exp_months:
        months = int(m_exp_months.group(1))
        return round(months/12.0, 2), []
    m_exp = re.search(r'Опыт\s+работ[ыи]\s*[:\-–—]?\s*([0-9]{1,2})\s*(?:год(?:а|ов)?|лет)(?:\s*([0-9]{1,2})\s*(?:месяц(?:а|ев)?))?', text, flags=re.IGNORECASE)
    if m_exp:
        yrs = int(m_exp.group(1))
        months = int(m_exp.group(2)) if m_exp.lastindex and m_exp.group(2) else 0
        return round(yrs + months/12.0, 2), []

    ranges = find_date_ranges(text)
    if not ranges:
        # Fallbacks: look for explicit total-experience phrases anywhere in the text
        # 1) patterns like 'Опыт работы —2 года 4 месяца' or '2 года 4 месяца' or '2 года'
        m = re.search(r'опыт\s+работ[ыи]\s*[:\-–—]?\s*([0-9]{1,2})\s*год', text, flags=re.IGNORECASE)
        if not m:
            m = re.search(r'([0-9]{1,2})\s*год(?:а|ов)?(?:\s*([0-9]{1,2})\s*месяц)?', text, flags=re.IGNORECASE)
        if m:
            yrs = int(m.group(1))
            months = 0
            if m.lastindex and m.lastindex >= 2 and m.group(2):
                try:
                    months = int(m.group(2))
                except Exception:
                    months = 0
            total = round(yrs + months/12.0, 2)
            return total, []
        # 2) months-only like '11 месяцев'
        m2 = re.search(r'([0-9]{1,2})\s*месяц(?:а|ев)?', text, flags=re.IGNORECASE)
        if m2:
            months = int(m2.group(1))
            total = round(months/12.0, 2)
            return total, []
        return None, []
    merged = merge_intervals(ranges)
    # compute total months
    total_months = 0
    for s,e in merged:
        # ensure start <= end; swap if inverted (PDF extraction can scramble order)
        if e < s:
            s, e = e, s
        # count months inclusive from s to e
        months = (e.year - s.year) * 12 + (e.month - s.month) + 1
        # ignore absurd ranges (>100 years) as noise
        if months < 0 or months > 100 * 12:
            continue
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



# Process all vacancy files
vacancy_files = get_pdf_files(VACANCY_DIR)
for vacancy_file in vacancy_files:
    vacancy_data = parse_file(vacancy_file)
    
    # Extract vacancy title from filename
    vacancy_filename = vacancy_data["filename"]
    title_match = re.search(r'[Оо]писание\s*(.*)\.pdf', vacancy_filename)
    vacancy_title = title_match.group(1).strip() if title_match else vacancy_filename.replace('.pdf','')

    vacancy_json = {
        "filename": vacancy_filename,
        "vacancy_info": {
            "title": vacancy_title,
            "required_experience_years": vacancy_data["vacancy_info"].get("required_experience_years"),
            # duties = Обязанности (for publication), responsibilities = Требования (for publication)
            "duties": vacancy_data["vacancy_info"].get("duties"),
            "responsibilities": vacancy_data["vacancy_info"].get("requirements")
        }
    }
    
    # Save each vacancy to a separate JSON file with its name
    output_file = OUTPUT_DIR / f"parsed_vacancy_{vacancy_title.lower().replace(' ', '_')}.json"
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(vacancy_json, f, ensure_ascii=False, indent=4)
    print(f"Saved vacancy JSON to: {output_file}")

# Process all resume files
resume_files = get_pdf_files(CV_DIR)
for resume_file in resume_files:
    resume_data = parse_file(resume_file)
    
    # Create simplified resume JSON with only required fields
    resume_json = {
        "filename": resume_data["filename"],
        "total_experience_years": resume_data["resume_info"]["total_experience_years"],
        "responsibilities": resume_data["resume_info"]["responsibilities"]
    }
    
    # Save each resume to a separate JSON file
    file_stem = Path(resume_data["filename"]).stem
    output_file = OUTPUT_DIR / f"parsed_resume_{file_stem.lower().replace(' ', '_')}.json"
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(resume_json, f, ensure_ascii=False, indent=4)
    print(f"Saved resume JSON to: {output_file}")
