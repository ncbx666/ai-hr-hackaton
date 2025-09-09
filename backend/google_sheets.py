# Заглушка для интеграции с Google Sheets
def write_result_to_sheet(interview_id: str, data: dict):
    """
    Записывает результаты интервью в Google Sheets
    """
    print(f"[MOCK] Запись результатов интервью {interview_id} в Google Sheets: {data}")
    return True
