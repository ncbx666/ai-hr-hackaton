"""
Google Sheets интеграция для HR системы
"""
import json
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime
import asyncio
import traceback
import os
from pathlib import Path

# Настройка расширенного логирования
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

# Создаем папку для логов если не существует
logs_dir = Path("logs")
logs_dir.mkdir(exist_ok=True)

# Настраиваем file handler для детальных логов Google Sheets
file_handler = logging.FileHandler(logs_dir / "google_sheets.log", encoding='utf-8')
file_handler.setLevel(logging.DEBUG)
file_formatter = logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s'
)
file_handler.setFormatter(file_formatter)
logger.addHandler(file_handler)

# Console handler для важных сообщений
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)
console_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
console_handler.setFormatter(console_formatter)
logger.addHandler(console_handler)

class GoogleSheetsService:
    """Сервис для работы с Google Sheets"""
    
    def __init__(self):
        # Для демонстрации используем простую интеграцию
        # В продакшене здесь будут настоящие API ключи Google Sheets
        self.sheets_api_key = "demo_key"
        self.demo_sheet_id = "1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OgvE2upms"
        self.operation_log = []  # Лог операций для отладки
        self.error_log = []      # Лог ошибок
        logger.info("[GoogleSheetsService] Инициализирован с расширенным логированием")
    
    def _log_operation(self, operation: str, data: Dict[str, Any], success: bool = True, error: str = None):
        """Логирует операцию Google Sheets"""
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "operation": operation,
            "data": data,
            "success": success,
            "error": error
        }
        
        self.operation_log.append(log_entry)
        
        # Ограничиваем размер лога (последние 100 операций)
        if len(self.operation_log) > 100:
            self.operation_log = self.operation_log[-100:]
        
        if success:
            logger.info(f"✅ Google Sheets операция успешна: {operation}")
            logger.debug(f"Детали операции: {json.dumps(data, ensure_ascii=False, indent=2)}")
        else:
            logger.error(f"❌ Google Sheets операция неуспешна: {operation}")
            logger.error(f"Ошибка: {error}")
            logger.debug(f"Данные операции: {json.dumps(data, ensure_ascii=False, indent=2)}")
            
            # Добавляем в лог ошибок
            error_entry = {
                "timestamp": datetime.now().isoformat(),
                "operation": operation,
                "error": error,
                "data": data,
                "traceback": traceback.format_exc() if error else None
            }
            self.error_log.append(error_entry)
            
            # Ограничиваем размер лога ошибок (последние 50 ошибок)
            if len(self.error_log) > 50:
                self.error_log = self.error_log[-50:]
    
    def get_operation_logs(self, limit: int = 20) -> List[Dict[str, Any]]:
        """Возвращает последние логи операций"""
        return self.operation_log[-limit:] if self.operation_log else []
    
    def get_error_logs(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Возвращает последние логи ошибок"""
        return self.error_log[-limit:] if self.error_log else []
    
    def get_statistics(self) -> Dict[str, Any]:
        """Возвращает статистику операций Google Sheets"""
        total_operations = len(self.operation_log)
        successful_operations = len([op for op in self.operation_log if op["success"]])
        failed_operations = total_operations - successful_operations
        
        recent_operations = self.operation_log[-10:] if self.operation_log else []
        
        return {
            "total_operations": total_operations,
            "successful_operations": successful_operations,
            "failed_operations": failed_operations,
            "success_rate": (successful_operations / total_operations * 100) if total_operations > 0 else 0,
            "recent_operations": recent_operations,
            "recent_errors": self.get_error_logs(5)
        }

    async def create_interview_sheet(self, interview_data: Dict[str, Any]) -> str:
        """
        Создает новую Google таблицу для собеседования
        Returns: URL таблицы
        """
        operation_data = {
            "interview_id": interview_data.get('id'),
            "position": interview_data.get('position'),
            "operation_type": "create_sheet"
        }
        
        try:
            logger.info(f"🚀 Начинаю создание Google таблицы для интервью {interview_data.get('id')}")
            
            # Симуляция создания Google Sheet
            sheet_id = f"interview_{interview_data.get('id', 'unknown')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            
            # Формируем URL Google таблицы
            sheets_url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/edit#gid=0"
            
            # Симуляция записи начальных данных
            initial_data = {
                "Интервью ID": interview_data.get('id'),
                "Позиция": interview_data.get('position'),
                "Дата создания": datetime.now().isoformat(),
                "Статус": "Создано",
                "Кандидат": "Ожидается",
                "Результат": "В процессе"
            }
            
            # В реальности здесь будет API вызов к Google Sheets
            await self._simulate_sheet_creation(sheet_id, initial_data)
            
            operation_data["sheet_id"] = sheet_id
            operation_data["sheets_url"] = sheets_url
            operation_data["initial_data"] = initial_data
            
            self._log_operation("create_interview_sheet", operation_data, success=True)
            logger.info(f"✅ Google таблица создана успешно: {sheets_url}")
            return sheets_url
            
        except Exception as e:
            error_msg = f"Ошибка создания Google таблицы: {e}"
            self._log_operation("create_interview_sheet", operation_data, success=False, error=error_msg)
            logger.error(f"❌ {error_msg}")
            logger.error(f"Traceback: {traceback.format_exc()}")
            
            # Возвращаем demo URL в случае ошибки
            fallback_url = f"https://docs.google.com/spreadsheets/d/demo_{interview_data.get('id')}/edit"
            logger.warning(f"🔄 Используем fallback URL: {fallback_url}")
            return fallback_url
    
    async def update_interview_results(self, interview_id: str, results_data: Dict[str, Any]) -> bool:
        """
        Обновляет результаты собеседования в Google таблице
        """
        operation_data = {
            "interview_id": interview_id,
            "operation_type": "update_results",
            "candidate_name": results_data.get('candidate_name'),
            "final_score": results_data.get('final_score_percent')
        }
        
        try:
            logger.info(f"🔄 Начинаю обновление результатов для интервью {interview_id}")
            
            # Подготовка данных для записи
            update_data = {
                "Кандидат": results_data.get('candidate_name', 'Неизвестно'),
                "Финальный балл": f"{results_data.get('final_score_percent', 0)}%",
                "Вердикт": results_data.get('verdict', 'Не определен'),
                "Технические навыки": f"{results_data.get('breakdown', {}).get('hard_skills', {}).get('score_percent', 0)}%",
                "Опыт работы": f"{results_data.get('breakdown', {}).get('experience', {}).get('score_percent', 0)}%",
                "Soft Skills": f"{results_data.get('breakdown', {}).get('soft_skills', {}).get('score_percent', 0)}%",
                "Дата обновления": datetime.now().isoformat()
            }
            
            # Симуляция обновления Google Sheet
            await self._simulate_sheet_update(interview_id, update_data)
            
            operation_data["update_data"] = update_data
            self._log_operation("update_interview_results", operation_data, success=True)
            
            logger.info(f"✅ Результаты успешно обновлены для интервью {interview_id}")
            return True
            
        except Exception as e:
            error_msg = f"Ошибка обновления результатов: {e}"
            self._log_operation("update_interview_results", operation_data, success=False, error=error_msg)
            logger.error(f"❌ {error_msg}")
            logger.error(f"Traceback: {traceback.format_exc()}")
            return False
    
    async def get_interview_sheet_url(self, interview_id: str) -> Optional[str]:
        """
        Получает URL Google таблицы для конкретного интервью
        """
        operation_data = {
            "interview_id": interview_id,
            "operation_type": "get_sheet_url"
        }
        
        try:
            logger.info(f"🔍 Получение URL таблицы для интервью {interview_id}")
            
            # В реальности здесь будет запрос к БД или Google Sheets API
            sheet_id = f"interview_{interview_id}"
            sheets_url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/edit#gid=0"
            
            operation_data["sheet_id"] = sheet_id
            operation_data["sheets_url"] = sheets_url
            
            self._log_operation("get_interview_sheet_url", operation_data, success=True)
            logger.info(f"✅ URL таблицы найден для интервью {interview_id}: {sheets_url}")
            return sheets_url
            
        except Exception as e:
            error_msg = f"Ошибка получения URL таблицы: {e}"
            self._log_operation("get_interview_sheet_url", operation_data, success=False, error=error_msg)
            logger.error(f"❌ {error_msg}")
            logger.error(f"Traceback: {traceback.format_exc()}")
            return None
    
    async def _simulate_sheet_creation(self, sheet_id: str, data: Dict[str, Any]):
        """Симуляция создания Google таблицы"""
        await asyncio.sleep(0.5)  # Имитация задержки API
        logger.debug(f"[GoogleSheetsService] Симуляция создания таблицы {sheet_id} с данными: {data}")
    
    async def _simulate_sheet_update(self, interview_id: str, data: Dict[str, Any]):
        """Симуляция обновления Google таблицы"""
        await asyncio.sleep(0.3)  # Имитация задержки API
        logger.debug(f"[GoogleSheetsService] Симуляция обновления таблицы для интервью {interview_id}: {data}")

# Глобальный экземпляр сервиса
google_sheets_service = GoogleSheetsService()
