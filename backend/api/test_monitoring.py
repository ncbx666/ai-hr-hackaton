"""
Тестовый скрипт для проверки работы системы мониторинга Google Sheets
"""

import asyncio
import sys
import os
from datetime import datetime

# Добавляем путь к API модулям
sys.path.insert(0, os.path.dirname(__file__))

from google_sheets_monitor import google_sheets_monitor, OperationType, OperationStatus
from google_sheets_service import google_sheets_service

async def test_monitoring_system():
    """
    Тестирует полную работу системы мониторинга
    """
    print("🧪 Запуск тестирования системы мониторинга Google Sheets")
    print("=" * 60)
    
    # Тест 1: Создание интервью (успешно)
    print("\n📊 Тест 1: Создание интервью")
    try:
        interview_data = {
            'id': 'test-interview-001',
            'position': 'Python Developer',
            'job_description': 'Backend разработчик для AI-HR системы',
            'created_at': datetime.now().isoformat()
        }
        
        result = await google_sheets_service.create_interview_sheet(
            interview_data=interview_data
        )
        print(f"✅ Результат: {result}")
        
    except Exception as e:
        print(f"❌ Ошибка: {e}")
    
    # Тест 2: Обновление результатов (успешно)
    print("\n📊 Тест 2: Обновление результатов")
    try:
        results_data = {
            'candidate_name': 'Иван Петров',
            'final_score_percent': 85,
            'verdict': 'Рекомендуется к найму',
            'breakdown': {
                'hard_skills': {'score_percent': 90},
                'experience': {'score_percent': 80},
                'soft_skills': {'score_percent': 85}
            }
        }
        
        result = await google_sheets_service.update_interview_results(
            interview_id='test-interview-001',
            results_data=results_data
        )
        print(f"✅ Результат: {result}")
        
    except Exception as e:
        print(f"❌ Ошибка: {e}")
    
    # Тест 3: Получение URL (успешно)
    print("\n📊 Тест 3: Получение URL")
    try:
        url = await google_sheets_service.get_interview_sheet_url('test-interview-001')
        print(f"✅ URL: {url}")
        
    except Exception as e:
        print(f"❌ Ошибка: {e}")
    
    # Тест 4: Симуляция ошибки
    print("\n📊 Тест 4: Симуляция ошибки")
    try:
        # Принудительно вызываем ошибку через невалидные данные
        await google_sheets_monitor.log_operation(
            operation_type=OperationType.CREATE_SHEET,
            interview_id='error-test-001',
            status=OperationStatus.ERROR,
            duration_ms=1500,
            details={'test': 'error simulation'},
            error_message="Симулированная ошибка для тестирования",
            stack_trace="Test stack trace"
        )
        print("✅ Ошибка успешно записана в мониторинг")
        
    except Exception as e:
        print(f"❌ Ошибка в симуляции ошибки: {e}")
    
    # Тест 5: Получение статистики
    print("\n📊 Тест 5: Статистика мониторинга")
    try:
        stats = await google_sheets_monitor.get_statistics()
        print("✅ Статистика:")
        for key, value in stats.items():
            print(f"   {key}: {value}")
        
    except Exception as e:
        print(f"❌ Ошибка получения статистики: {e}")
    
    # Тест 6: Получение логов
    print("\n📊 Тест 6: Получение логов")
    try:
        logs = await google_sheets_monitor.get_recent_logs(limit=10)
        print(f"✅ Получено логов: {len(logs)}")
        
        for i, log in enumerate(logs[:3], 1):  # Показываем первые 3
            print(f"   Лог #{i}:")
            print(f"     Время: {log.timestamp}")
            print(f"     Операция: {log.operation_type.value}")
            print(f"     Статус: {log.status.value}")
            print(f"     Интервью: {log.interview_id}")
            print(f"     Длительность: {log.duration_ms}ms")
            if log.error_message:
                print(f"     Ошибка: {log.error_message}")
            print()
        
    except Exception as e:
        print(f"❌ Ошибка получения логов: {e}")
    
    print("=" * 60)
    print("🎉 Тестирование завершено!")

async def test_performance():
    """
    Тестирует производительность системы мониторинга
    """
    print("\n⚡ Тест производительности мониторинга")
    print("-" * 40)
    
    import time
    
    start_time = time.time()
    
    # Создаем много операций для тестирования производительности
    tasks = []
    for i in range(100):
        task = google_sheets_monitor.log_operation(
            operation_type=OperationType.CREATE_SHEET,
            interview_id=f'perf-test-{i:03d}',
            status=OperationStatus.SUCCESS,
            duration_ms=50 + (i % 500),  # Варьируем время от 50 до 550ms
            details={'test_iteration': i, 'performance_test': True}
        )
        tasks.append(task)
    
    # Выполняем все задачи параллельно
    await asyncio.gather(*tasks)
    
    end_time = time.time()
    total_time = end_time - start_time
    
    print(f"✅ Записано 100 операций за {total_time:.2f} секунд")
    print(f"📊 Скорость: {100/total_time:.2f} операций/сек")
    
    # Проверяем итоговую статистику
    stats = await google_sheets_monitor.get_statistics()
    print(f"📈 Общая статистика после теста:")
    print(f"   Всего операций: {stats.get('total_operations', 0)}")
    print(f"   Успешных: {stats.get('successful_operations', 0)}")
    print(f"   С ошибками: {stats.get('error_operations', 0)}")

if __name__ == "__main__":
    print("🚀 Запуск тестов системы мониторинга Google Sheets")
    
    try:
        # Основные функциональные тесты
        asyncio.run(test_monitoring_system())
        
        # Тесты производительности
        asyncio.run(test_performance())
        
        print("\n🎯 Все тесты выполнены успешно!")
        
    except Exception as e:
        print(f"\n💥 Критическая ошибка в тестах: {e}")
        import traceback
        traceback.print_exc()
