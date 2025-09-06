import gspread
from oauth2client.service_account import ServiceAccountCredentials

# Настройка доступа к Google Sheets
scope = [
    'https://spreadsheets.google.com/feeds',
    'https://www.googleapis.com/auth/drive'
]
creds = ServiceAccountCredentials.from_json_keyfile_name('google-credentials.json', scope)
client = gspread.authorize(creds)

# ID таблицы (замени на свой)
SPREADSHEET_ID = '1e0T4eh4vx9hzXdXffs3f6I-ktaVhmwvW7O5Ls31w7Ac'

# Запись строки с результатами
def write_result_to_sheet(data: dict):
    sheet = client.open_by_key(SPREADSHEET_ID).sheet1
    # Пример: записать имя, позицию, баллы, комментарий
    row = [
        data.get('candidate_name', ''),
        data.get('position', ''),
        data.get('score', ''),
        data.get('comment', '')
    ]
    sheet.append_row(row)
    return True

# Пример использования:
# write_result_to_sheet({
#     'candidate_name': 'Иванов Иван',
#     'position': 'Frontend',
#     'score': 85,
#     'comment': 'Рекомендован'
# })
