# Система мониторинга Google Sheets

## Обзор

Система мониторинга предоставляет комплексное отслеживание операций с Google Sheets в AI-HR приложении, включая:

- 📊 **Детальное логирование** всех операций
- ⚡ **Мониторинг производительности** с измерением времени выполнения
- 🚨 **Отслеживание ошибок** с полными stack trace
- 📈 **Статистика и аналитика** операций
- 🔍 **API для мониторинга** в реальном времени

## Архитектура

### Основные компоненты

1. **GoogleSheetsMonitor** (`google_sheets_monitor.py`)
   - Центральная система логирования
   - Файловое и in-memory хранение логов
   - Асинхронная обработка операций

2. **GoogleSheetsService** (`google_sheets_service.py`)
   - Интеграция с системой мониторинга
   - Автоматическое логирование всех операций
   - Измерение производительности

3. **Monitoring API** (`monitoring_endpoints.py`)
   - REST API для доступа к данным мониторинга
   - Фильтрация и поиск по логам
   - Статистика и аналитика

## Типы операций

```python
class OperationType(Enum):
    CREATE_SHEET = "create_sheet"        # Создание таблицы
    UPDATE_RESULTS = "update_results"    # Обновление результатов
    GET_URL = "get_url"                  # Получение URL таблицы
```

## Статусы операций

```python
class OperationStatus(Enum):
    SUCCESS = "success"  # Успешное выполнение
    ERROR = "error"      # Ошибка выполнения
```

## API эндпоинты

### Основная информация

- `GET /api/monitor/google-sheets/status` - Общий статус мониторинга
- `GET /api/monitor/google-sheets/statistics` - Детальная статистика

### Логи и ошибки

- `GET /api/monitor/google-sheets/logs` - Получение логов с фильтрацией
- `GET /api/monitor/google-sheets/errors` - Только логи с ошибками
- `DELETE /api/monitor/google-sheets/logs` - Очистка старых логов

### Производительность

- `GET /api/monitor/google-sheets/performance` - Метрики производительности

## Примеры использования

### 1. Получение общей статистики

```bash
GET /api/monitor/google-sheets/status
```

Ответ:
```json
{
  "status": "active",
  "monitoring_enabled": true,
  "statistics": {
    "total_operations": 150,
    "successful_operations": 142,
    "error_operations": 8,
    "success_rate": 94.67,
    "avg_duration_ms": 245.5
  },
  "timestamp": "2024-01-20T10:30:00"
}
```

### 2. Получение логов с фильтрацией

```bash
GET /api/monitor/google-sheets/logs?operation_type=create_sheet&status=error&limit=10
```

Ответ:
```json
{
  "logs": [
    {
      "timestamp": "2024-01-20T10:25:00",
      "operation_type": "create_sheet",
      "interview_id": "interview-123",
      "status": "error",
      "duration_ms": 1500,
      "error_message": "Google Sheets API rate limit exceeded",
      "has_stack_trace": true
    }
  ],
  "total_count": 1,
  "filters_applied": {
    "operation_type": "create_sheet",
    "status": "error",
    "hours_back": 24
  }
}
```

### 3. Анализ производительности

```bash
GET /api/monitor/google-sheets/performance?hours=24
```

Ответ:
```json
{
  "performance_metrics": {
    "create_sheet": {
      "total_operations": 45,
      "success_rate": 95.56,
      "avg_duration_ms": 234.5,
      "min_duration_ms": 150,
      "max_duration_ms": 890,
      "median_duration_ms": 220,
      "p95_duration_ms": 456,
      "p99_duration_ms": 678
    }
  }
}
```

## Настройка и запуск

### 1. Установка зависимостей

Система автоматически работает с существующими зависимостями FastAPI проекта.

### 2. Запуск тестов

```bash
cd backend/api
python test_monitoring.py
```

### 3. Запуск API сервера

```bash
cd backend/api
python main.py
```

API будет доступно по адресу: `http://localhost:8000`

Документация Swagger: `http://localhost:8000/docs`

## Конфигурация

### Настройки логирования

```python
# В google_sheets_monitor.py
LOG_FILE_PATH = "logs/google_sheets_operations.log"
MAX_IN_MEMORY_LOGS = 1000
```

### Настройки API

```python
# Фильтрация логов
DEFAULT_LOG_LIMIT = 50
MAX_LOG_LIMIT = 1000
DEFAULT_HOURS_BACK = 24
MAX_HOURS_BACK = 168  # 7 дней
```

## Структура логов

Каждая запись лога содержит:

```python
@dataclass
class LogEntry:
    timestamp: datetime           # Время операции
    operation_type: OperationType # Тип операции
    interview_id: str            # ID интервью
    status: OperationStatus      # Статус выполнения
    duration_ms: Optional[int]   # Время выполнения в мс
    details: Dict[str, Any]      # Дополнительные данные
    error_message: Optional[str] # Сообщение об ошибке
    stack_trace: Optional[str]   # Stack trace ошибки
```

## Мониторинг в реальном времени

### Dashboard endpoints

- `/api/monitor/google-sheets/status` - Статус системы
- `/api/monitor/google-sheets/logs?limit=10` - Последние операции
- `/api/monitor/google-sheets/errors?hours=1` - Недавние ошибки

### Алерты и уведомления

Система готова для интеграции с системами алертов:

1. **Высокий процент ошибок** (>10% за час)
2. **Медленные операции** (>1000ms)
3. **Недоступность Google Sheets API**

## Интеграция с Google Sheets Service

Все методы `GoogleSheetsService` автоматически интегрированы с мониторингом:

```python
# Автоматически логируется
await google_sheets_service.create_interview_sheet(interview_id, data)
await google_sheets_service.update_interview_results(interview_id, results)
await google_sheets_service.get_interview_sheet_url(interview_id)
```

## Производительность

- **Асинхронная обработка** - не блокирует основные операции
- **Батчевая запись** - эффективное сохранение логов
- **In-memory кэширование** - быстрый доступ к статистике
- **Автоматическая ротация логов** - управление размером файлов

## Безопасность

- Логирование не содержит чувствительных данных
- Stack traces ограничены для production
- API endpoints защищены от DoS через rate limiting

## Разработка и отладка

### Локальное тестирование

```bash
# Запуск всех тестов
python test_monitoring.py

# Проверка API
curl http://localhost:8000/api/monitor/google-sheets/status
```

### Логирование

Включено детальное логирование для отладки:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## Планы развития

1. **Интеграция с Grafana** для визуализации метрик
2. **Webhook уведомления** при критических ошибках  
3. **Автоматическое восстановление** после сбоев API
4. **Machine Learning** для предсказания проблем
5. **Экспорт метрик** в Prometheus формат

---

*Система мониторинга Google Sheets v1.0 - AI-HR Hackaton 2024*
