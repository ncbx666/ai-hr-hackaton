import os
import json
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime
from typing import Dict, List, Any, Optional
import logging

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class GoogleSheetsService:
    def __init__(self):
        self.scope = ['https://spreadsheets.google.com/feeds',
                     'https://www.googleapis.com/auth/drive']
        self.client = None
        self.operation_log = []  # Список операций
        self.error_log = []      # Список ошибок
        self.log_file = "google_sheets_operations.log"
        
        # Инициализация клиента
        self._init_client()
    
    def _init_client(self):
        """Инициализация Google Sheets клиента"""
        try:
            # Путь к файлу учетных данных
            credentials_path = os.environ.get('GOOGLE_SHEETS_CREDENTIALS', 'credentials.json')
            
            if os.path.exists(credentials_path):
                creds = ServiceAccountCredentials.from_json_keyfile_name(
                    credentials_path, self.scope
                )
                self.client = gspread.authorize(creds)
                self._log_operation("init", "success", "Google Sheets клиент инициализирован")
            else:
                self._log_operation("init", "error", f"Файл учетных данных не найден: {credentials_path}")
                logger.warning(f"Google Sheets credentials не найдены по пути: {credentials_path}")
        except Exception as e:
            self._log_operation("init", "error", f"Ошибка инициализации: {str(e)}")
            logger.error(f"Ошибка инициализации Google Sheets: {e}")
    
    def _log_operation(self, operation: str, status: str, details: str = "", data: dict = None):
        """Логирование операций"""
        timestamp = datetime.now().isoformat()
        log_entry = {
            "timestamp": timestamp,
            "operation": operation,
            "status": status,
            "details": details,
            "data": data
        }
        
        # Добавляем в память
        self.operation_log.append(log_entry)
        
        # Если ошибка, добавляем в лог ошибок
        if status == "error":
            self.error_log.append(log_entry)
        
        # Записываем в файл
        try:
            with open(self.log_file, "a", encoding="utf-8") as f:
                f.write(f"{json.dumps(log_entry, ensure_ascii=False)}\n")
        except Exception as e:
            logger.error(f"Ошибка записи в лог файл: {e}")
        
        # Ограничиваем размер логов в памяти
        if len(self.operation_log) > 1000:
            self.operation_log = self.operation_log[-500:]
        if len(self.error_log) > 100:
            self.error_log = self.error_log[-50:]
    
    def get_operation_logs(self, limit: int = 50) -> List[Dict]:
        """Получить логи операций"""
        return self.operation_log[-limit:]
    
    def get_error_logs(self, limit: int = 20) -> List[Dict]:
        """Получить логи ошибок"""
        return self.error_log[-limit:]
    
    def get_statistics(self) -> Dict:
        """Получить статистику операций"""
        total_operations = len(self.operation_log)
        total_errors = len(self.error_log)
        success_rate = ((total_operations - total_errors) / total_operations * 100) if total_operations > 0 else 0
        
        # Статистика по типам операций
        operation_types = {}
        for log in self.operation_log:
            op_type = log["operation"]
            if op_type not in operation_types:
                operation_types[op_type] = {"total": 0, "success": 0, "error": 0}
            operation_types[op_type]["total"] += 1
            if log["status"] == "success":
                operation_types[op_type]["success"] += 1
            else:
                operation_types[op_type]["error"] += 1
        
        return {
            "total_operations": total_operations,
            "total_errors": total_errors,
            "success_rate": round(success_rate, 2),
            "client_status": "connected" if self.client else "disconnected",
            "operation_types": operation_types,
            "last_operation": self.operation_log[-1] if self.operation_log else None
        }
    
    def create_spreadsheet(self, title: str, interview_data: dict) -> Optional[str]:
        """Создание нового Google Sheets документа"""
        try:
            if not self.client:
                self._log_operation("create_spreadsheet", "error", "Google Sheets клиент не инициализирован")
                return None
            
            # Создаем новый документ
            sheet = self.client.create(title)
            spreadsheet_id = sheet.id
            
            # Делаем документ публично доступным для чтения
            sheet.share('', perm_type='anyone', role='reader')
            
            # Получаем первый лист
            worksheet = sheet.get_worksheet(0)
            
            # Устанавливаем заголовки
            headers = [
                'ID интервью', 'Должность', 'Кандидат', 'Дата создания',
                'Статус', 'Общий балл', 'Технические навыки', 'Soft skills',
                'Опыт работы', 'Образование', 'Комментарии', 'Рекомендация'
            ]
            worksheet.append_row(headers)
            
            # Добавляем данные интервью
            row_data = [
                interview_data.get('id', ''),
                interview_data.get('position', ''),
                interview_data.get('candidate_name', ''),
                datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                interview_data.get('status', 'В процессе'),
                '', '', '', '', '', '', ''  # Пустые поля для результатов
            ]
            worksheet.append_row(row_data)
            
            self._log_operation(
                "create_spreadsheet", 
                "success", 
                f"Создан документ: {title}",
                {"spreadsheet_id": spreadsheet_id, "title": title}
            )
            
            return spreadsheet_id
            
        except Exception as e:
            self._log_operation(
                "create_spreadsheet", 
                "error", 
                f"Ошибка создания документа: {str(e)}",
                {"title": title}
            )
            logger.error(f"Ошибка создания Google Sheets: {e}")
            return None
    
    def update_interview_results(self, spreadsheet_id: str, interview_data: dict) -> bool:
        """Обновление результатов интервью в Google Sheets"""
        try:
            if not self.client:
                self._log_operation("update_results", "error", "Google Sheets клиент не инициализирован")
                return False
            
            # Открываем документ
            sheet = self.client.open_by_key(spreadsheet_id)
            worksheet = sheet.get_worksheet(0)
            
            # Находим строку с нужным ID интервью
            all_records = worksheet.get_all_records()
            row_index = None
            
            for i, record in enumerate(all_records):
                if record.get('ID интервью') == interview_data.get('id'):
                    row_index = i + 2  # +2 потому что enumerate начинается с 0, а в Google Sheets с 1, плюс заголовок
                    break
            
            if row_index is None:
                self._log_operation(
                    "update_results", 
                    "error", 
                    f"Интервью с ID {interview_data.get('id')} не найдено"
                )
                return False
            
            # Обновляем данные
            updates = []
            if 'status' in interview_data:
                updates.append(('E', row_index, interview_data['status']))
            if 'overall_score' in interview_data:
                updates.append(('F', row_index, interview_data['overall_score']))
            if 'technical_skills' in interview_data:
                updates.append(('G', row_index, interview_data['technical_skills']))
            if 'soft_skills' in interview_data:
                updates.append(('H', row_index, interview_data['soft_skills']))
            if 'experience' in interview_data:
                updates.append(('I', row_index, interview_data['experience']))
            if 'education' in interview_data:
                updates.append(('J', row_index, interview_data['education']))
            if 'comments' in interview_data:
                updates.append(('K', row_index, interview_data['comments']))
            if 'recommendation' in interview_data:
                updates.append(('L', row_index, interview_data['recommendation']))
            
            # Применяем обновления
            for col, row, value in updates:
                worksheet.update(f'{col}{row}', value)
            
            self._log_operation(
                "update_results", 
                "success", 
                f"Обновлены результаты интервью {interview_data.get('id')}",
                {"spreadsheet_id": spreadsheet_id, "updates_count": len(updates)}
            )
            
            return True
            
        except Exception as e:
            self._log_operation(
                "update_results", 
                "error", 
                f"Ошибка обновления результатов: {str(e)}",
                {"spreadsheet_id": spreadsheet_id}
            )
            logger.error(f"Ошибка обновления Google Sheets: {e}")
            return False
    
    def get_spreadsheet_data(self, spreadsheet_id: str) -> Optional[Dict]:
        """Получение данных из Google Sheets"""
        try:
            if not self.client:
                self._log_operation("get_data", "error", "Google Sheets клиент не инициализирован")
                return None
            
            # Открываем документ
            sheet = self.client.open_by_key(spreadsheet_id)
            worksheet = sheet.get_worksheet(0)
            
            # Получаем все записи
            records = worksheet.get_all_records()
            
            self._log_operation(
                "get_data", 
                "success", 
                f"Получены данные из документа",
                {"spreadsheet_id": spreadsheet_id, "records_count": len(records)}
            )
            
            return {
                "spreadsheet_id": spreadsheet_id,
                "title": sheet.title,
                "records": records,
                "url": f"https://docs.google.com/spreadsheets/d/{spreadsheet_id}"
            }
            
        except Exception as e:
            self._log_operation(
                "get_data", 
                "error", 
                f"Ошибка получения данных: {str(e)}",
                {"spreadsheet_id": spreadsheet_id}
            )
            logger.error(f"Ошибка получения данных из Google Sheets: {e}")
            return None

# Создаем глобальный экземпляр сервиса
google_sheets_service = GoogleSheetsService()

# Заглушка для обратной совместимости
def write_result_to_sheet(interview_id: str, data: dict):
    """
    Записывает результаты интервью в Google Sheets
    """
    print(f"[MOCK] Запись результатов интервью {interview_id} в Google Sheets: {data}")
    return True
