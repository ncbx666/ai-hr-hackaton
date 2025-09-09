"""
Система логирования и мониторинга для Google Sheets интеграции
"""
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from pathlib import Path
import asyncio
from dataclasses import dataclass, asdict
from enum import Enum

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('google_sheets_monitor.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger('GoogleSheetsMonitor')

class OperationType(Enum):
    CREATE_SHEET = "create_sheet"
    UPDATE_RESULTS = "update_results"
    GET_URL = "get_url"
    DELETE_SHEET = "delete_sheet"

class OperationStatus(Enum):
    SUCCESS = "success"
    ERROR = "error"
    PENDING = "pending"
    TIMEOUT = "timeout"

@dataclass
class LogEntry:
    """Структура для записи лога операции"""
    timestamp: str
    operation_type: OperationType
    interview_id: str
    status: OperationStatus
    duration_ms: int
    details: Dict[str, Any]
    error_message: Optional[str] = None
    stack_trace: Optional[str] = None

class GoogleSheetsMonitor:
    """Система мониторинга операций с Google Sheets"""
    
    def __init__(self):
        self.logs: List[LogEntry] = []
        self.max_logs = 1000  # Максимум записей в памяти
        self.log_file = Path("logs/google_sheets_operations.json")
        self.log_file.parent.mkdir(exist_ok=True)
        
        # Статистика
        self.stats = {
            "total_operations": 0,
            "successful_operations": 0,
            "failed_operations": 0,
            "average_response_time": 0.0,
            "last_error": None,
            "operations_by_type": {op.value: 0 for op in OperationType},
            "errors_by_type": {op.value: 0 for op in OperationType}
        }
        
        logger.info("[GoogleSheetsMonitor] Инициализирован")
    
    async def log_operation(self, 
                          operation_type: OperationType,
                          interview_id: str,
                          status: OperationStatus,
                          duration_ms: int,
                          details: Dict[str, Any],
                          error_message: Optional[str] = None,
                          stack_trace: Optional[str] = None):
        """Записывает операцию в лог"""
        
        entry = LogEntry(
            timestamp=datetime.now().isoformat(),
            operation_type=operation_type,
            interview_id=interview_id,
            status=status,
            duration_ms=duration_ms,
            details=details,
            error_message=error_message,
            stack_trace=stack_trace
        )
        
        # Добавляем в память
        self.logs.append(entry)
        
        # Ограничиваем размер логов в памяти
        if len(self.logs) > self.max_logs:
            self.logs.pop(0)
        
        # Обновляем статистику
        self._update_stats(entry)
        
        # Сохраняем в файл
        await self._save_to_file(entry)
        
        # Логируем в консоль
        if status == OperationStatus.ERROR:
            logger.error(f"[{operation_type.value}] {interview_id}: {error_message}")
        else:
            logger.info(f"[{operation_type.value}] {interview_id}: {status.value} ({duration_ms}ms)")
    
    def _update_stats(self, entry: LogEntry):
        """Обновляет статистику"""
        self.stats["total_operations"] += 1
        self.stats["operations_by_type"][entry.operation_type.value] += 1
        
        if entry.status == OperationStatus.SUCCESS:
            self.stats["successful_operations"] += 1
        elif entry.status == OperationStatus.ERROR:
            self.stats["failed_operations"] += 1
            self.stats["errors_by_type"][entry.operation_type.value] += 1
            self.stats["last_error"] = {
                "timestamp": entry.timestamp,
                "operation": entry.operation_type.value,
                "interview_id": entry.interview_id,
                "message": entry.error_message
            }
        
        # Обновляем среднее время ответа
        if entry.status == OperationStatus.SUCCESS:
            total_success = self.stats["successful_operations"]
            current_avg = self.stats["average_response_time"]
            self.stats["average_response_time"] = (
                (current_avg * (total_success - 1) + entry.duration_ms) / total_success
            )
    
    async def _save_to_file(self, entry: LogEntry):
        """Сохраняет запись в файл"""
        try:
            # Читаем существующие логи
            if self.log_file.exists():
                with open(self.log_file, 'r', encoding='utf-8') as f:
                    existing_logs = json.load(f)
            else:
                existing_logs = []
            
            # Добавляем новую запись с правильной сериализацией Enum
            log_dict = asdict(entry)
            log_dict['operation_type'] = entry.operation_type.value
            log_dict['status'] = entry.status.value
            existing_logs.append(log_dict)
            
            # Ограничиваем размер файла (последние 5000 записей)
            if len(existing_logs) > 5000:
                existing_logs = existing_logs[-5000:]
            
            # Сохраняем обратно
            with open(self.log_file, 'w', encoding='utf-8') as f:
                json.dump(existing_logs, f, ensure_ascii=False, indent=2)
                
        except Exception as e:
            logger.error(f"Ошибка сохранения лога в файл: {e}")
    
    def get_recent_logs(self, limit: int = 100) -> List[Dict]:
        """Возвращает последние логи"""
        return [asdict(log) for log in self.logs[-limit:]]
    
    def get_error_logs(self, limit: int = 50) -> List[Dict]:
        """Возвращает последние ошибки"""
        error_logs = [log for log in self.logs if log.status == OperationStatus.ERROR]
        return [asdict(log) for log in error_logs[-limit:]]
    
    def get_stats(self) -> Dict[str, Any]:
        """Возвращает статистику"""
        return {
            **self.stats,
            "success_rate": (
                self.stats["successful_operations"] / max(self.stats["total_operations"], 1) * 100
            ),
            "error_rate": (
                self.stats["failed_operations"] / max(self.stats["total_operations"], 1) * 100
            )
        }
    
    async def get_statistics(self) -> Dict[str, Any]:
        """Асинхронная версия получения статистики для совместимости с API"""
        return self.get_stats()
    
    async def get_recent_logs(self, limit: int = 100, **filters) -> List[LogEntry]:
        """Асинхронная версия получения логов с фильтрами"""
        filtered_logs = self.logs.copy()
        
        # Применяем фильтры
        if 'operation_type' in filters:
            filtered_logs = [log for log in filtered_logs if log.operation_type == filters['operation_type']]
        
        if 'status' in filters:
            filtered_logs = [log for log in filtered_logs if log.status == filters['status']]
        
        if 'interview_id' in filters:
            filtered_logs = [log for log in filtered_logs if log.interview_id == filters['interview_id']]
        
        if 'since' in filters:
            since = filters['since']
            filtered_logs = [log for log in filtered_logs if datetime.fromisoformat(log.timestamp) >= since]
        
        # Сортируем по времени (новые сначала) и ограничиваем
        filtered_logs.sort(key=lambda x: datetime.fromisoformat(x.timestamp), reverse=True)
        return filtered_logs[:limit]
    
    def get_logs_by_interview(self, interview_id: str) -> List[Dict]:
        """Возвращает логи для конкретного интервью"""
        interview_logs = [log for log in self.logs if log.interview_id == interview_id]
        return [asdict(log) for log in interview_logs]
    
    def get_logs_by_timeframe(self, hours: int = 24) -> List[Dict]:
        """Возвращает логи за последние N часов"""
        cutoff_time = datetime.now() - timedelta(hours=hours)
        recent_logs = []
        
        for log in self.logs:
            log_time = datetime.fromisoformat(log.timestamp)
            if log_time >= cutoff_time:
                recent_logs.append(asdict(log))
        
        return recent_logs
    
    def clear_old_logs(self, days: int = 7):
        """Очищает логи старше N дней"""
        cutoff_time = datetime.now() - timedelta(days=days)
        self.logs = [
            log for log in self.logs 
            if datetime.fromisoformat(log.timestamp) >= cutoff_time
        ]
        logger.info(f"Очищены логи старше {days} дней")

# Глобальный экземпляр монитора
google_sheets_monitor = GoogleSheetsMonitor()
