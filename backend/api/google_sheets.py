import gspread
from oauth2client.service_account import ServiceAccountCredentials
import os

# Настройка доступа к Google Sheets
def get_google_sheets_client():
    """Получение клиента Google Sheets с проверкой credentials"""
    try:
        scope = [
            'https://spreadsheets.google.com/feeds',
            'https://www.googleapis.com/auth/drive'
        ]
        
        credentials_path = os.getenv('GOOGLE_SHEETS_CREDENTIALS', 'google-credentials.json')
        
        if not os.path.exists(credentials_path):
            print(f"[Google Sheets] Credentials file not found: {credentials_path}")
            return None
            
        creds = ServiceAccountCredentials.from_json_keyfile_name(credentials_path, scope)
        client = gspread.authorize(creds)
        return client
    except Exception as e:
        print(f"[Google Sheets] Error initializing client: {e}")
        return None

# ID таблицы (замени на свой)
SPREADSHEET_ID = os.getenv('SPREADSHEET_ID', '1e0T4eh4vx9hzXdXffs3f6I-ktaVhmwvW7O5Ls31w7Ac')

# Запись строки с результатами
def write_result_to_sheet(data: dict):
    """Запись результатов в Google Sheets"""
    try:
        client = get_google_sheets_client()
        if not client:
            print("[Google Sheets] Client not available, skipping write")
            return False
            
        sheet = client.open_by_key(SPREADSHEET_ID).sheet1
        # Пример: записать имя, позицию, баллы, комментарий
        row = [
            data.get('candidate_name', ''),
            data.get('position', ''),
            data.get('score', 0),
            data.get('comments', ''),
            data.get('timestamp', '')
        ]
        sheet.append_row(row)
        print(f"[Google Sheets] Successfully wrote result for {data.get('candidate_name', 'Unknown')}")
        return True
    except Exception as e:
        print(f"[Google Sheets] Error writing to sheet: {e}")
        return False

# Пример использования:
# write_result_to_sheet({
#     'candidate_name': 'Иванов Иван',
#     'position': 'Frontend',
#     'score': 85,
#     'comment': 'Рекомендован'
# })
