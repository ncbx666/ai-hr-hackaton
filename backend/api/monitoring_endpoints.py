"""
API эндпоинты для мониторинга Google Sheets операций
"""

from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import JSONResponse
from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta

from .google_sheets_monitor import google_sheets_monitor, OperationType, OperationStatus

router = APIRouter(prefix="/api/monitor", tags=["monitoring"])

@router.get("/google-sheets/status")
async def get_monitoring_status():
    """
    Получить общий статус мониторинга Google Sheets
    """
    try:
        stats = await google_sheets_monitor.get_statistics()
        
        return JSONResponse({
            "status": "active",
            "monitoring_enabled": True,
            "statistics": stats,
            "timestamp": datetime.now().isoformat()
        })
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка получения статуса: {str(e)}")

@router.get("/google-sheets/logs")
async def get_operation_logs(
    limit: int = Query(50, ge=1, le=1000, description="Количество записей для возврата"),
    operation_type: Optional[str] = Query(None, description="Фильтр по типу операции"),
    status: Optional[str] = Query(None, description="Фильтр по статусу операции"),
    interview_id: Optional[str] = Query(None, description="Фильтр по ID интервью"),
    hours: Optional[int] = Query(24, ge=1, le=168, description="Количество часов назад для поиска")
):
    """
    Получить логи операций Google Sheets с фильтрацией
    """
    try:
        # Формируем фильтры
        filters = {}
        
        if operation_type:
            try:
                filters["operation_type"] = OperationType(operation_type)
            except ValueError:
                raise HTTPException(status_code=400, detail=f"Неверный тип операции: {operation_type}")
        
        if status:
            try:
                filters["status"] = OperationStatus(status)
            except ValueError:
                raise HTTPException(status_code=400, detail=f"Неверный статус: {status}")
        
        if interview_id:
            filters["interview_id"] = interview_id
        
        # Временной фильтр
        since = datetime.now() - timedelta(hours=hours)
        filters["since"] = since
        
        # Получаем логи
        logs = await google_sheets_monitor.get_recent_logs(limit=limit, **filters)
        
        # Преобразуем логи в JSON-совместимый формат
        logs_data = []
        for log in logs:
            log_dict = {
                "timestamp": log.timestamp.isoformat(),
                "operation_type": log.operation_type.value,
                "interview_id": log.interview_id,
                "status": log.status.value,
                "duration_ms": log.duration_ms,
                "details": log.details,
                "error_message": log.error_message,
                "has_stack_trace": bool(log.stack_trace)
            }
            logs_data.append(log_dict)
        
        return JSONResponse({
            "logs": logs_data,
            "total_count": len(logs_data),
            "filters_applied": {
                "operation_type": operation_type,
                "status": status,
                "interview_id": interview_id,
                "hours_back": hours
            },
            "timestamp": datetime.now().isoformat()
        })
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка получения логов: {str(e)}")

@router.get("/google-sheets/statistics")
async def get_detailed_statistics(
    hours: int = Query(24, ge=1, le=168, description="Период для статистики в часах")
):
    """
    Получить детальную статистику операций Google Sheets
    """
    try:
        # Базовая статистика
        stats = await google_sheets_monitor.get_statistics()
        
        # Статистика за период
        since = datetime.now() - timedelta(hours=hours)
        recent_logs = await google_sheets_monitor.get_recent_logs(limit=1000, since=since)
        
        # Анализируем статистику по типам операций
        operation_stats = {}
        status_stats = {}
        performance_stats = {
            "total_operations": len(recent_logs),
            "avg_duration_ms": 0,
            "max_duration_ms": 0,
            "min_duration_ms": float('inf') if recent_logs else 0
        }
        
        durations = []
        for log in recent_logs:
            # Статистика по типам операций
            op_type = log.operation_type.value
            if op_type not in operation_stats:
                operation_stats[op_type] = {"total": 0, "success": 0, "error": 0}
            
            operation_stats[op_type]["total"] += 1
            if log.status == OperationStatus.SUCCESS:
                operation_stats[op_type]["success"] += 1
            else:
                operation_stats[op_type]["error"] += 1
            
            # Статистика по статусам
            status = log.status.value
            status_stats[status] = status_stats.get(status, 0) + 1
            
            # Статистика производительности
            if log.duration_ms is not None:
                durations.append(log.duration_ms)
                performance_stats["max_duration_ms"] = max(
                    performance_stats["max_duration_ms"], 
                    log.duration_ms
                )
                performance_stats["min_duration_ms"] = min(
                    performance_stats["min_duration_ms"], 
                    log.duration_ms
                )
        
        if durations:
            performance_stats["avg_duration_ms"] = sum(durations) / len(durations)
        if performance_stats["min_duration_ms"] == float('inf'):
            performance_stats["min_duration_ms"] = 0
        
        return JSONResponse({
            "period_hours": hours,
            "base_statistics": stats,
            "operation_statistics": operation_stats,
            "status_statistics": status_stats,
            "performance_statistics": performance_stats,
            "timestamp": datetime.now().isoformat()
        })
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка получения статистики: {str(e)}")

@router.get("/google-sheets/errors")
async def get_error_logs(
    limit: int = Query(50, ge=1, le=500, description="Количество ошибок для возврата"),
    hours: int = Query(24, ge=1, le=168, description="Период поиска ошибок в часах")
):
    """
    Получить логи только с ошибками
    """
    try:
        since = datetime.now() - timedelta(hours=hours)
        
        # Получаем логи только с ошибками
        error_logs = await google_sheets_monitor.get_recent_logs(
            limit=limit,
            status=OperationStatus.ERROR,
            since=since
        )
        
        # Группируем ошибки по типам
        error_groups = {}
        
        for log in error_logs:
            error_type = log.error_message.split(":")[0] if log.error_message else "Unknown"
            
            if error_type not in error_groups:
                error_groups[error_type] = {
                    "count": 0,
                    "latest_occurrence": None,
                    "affected_interviews": set(),
                    "example_error": None
                }
            
            error_groups[error_type]["count"] += 1
            error_groups[error_type]["affected_interviews"].add(log.interview_id)
            
            if (error_groups[error_type]["latest_occurrence"] is None or 
                log.timestamp > error_groups[error_type]["latest_occurrence"]):
                error_groups[error_type]["latest_occurrence"] = log.timestamp
                error_groups[error_type]["example_error"] = {
                    "timestamp": log.timestamp.isoformat(),
                    "interview_id": log.interview_id,
                    "operation_type": log.operation_type.value,
                    "error_message": log.error_message,
                    "has_stack_trace": bool(log.stack_trace)
                }
        
        # Преобразуем для JSON
        for group in error_groups.values():
            group["affected_interviews"] = list(group["affected_interviews"])
            if group["latest_occurrence"]:
                group["latest_occurrence"] = group["latest_occurrence"].isoformat()
        
        return JSONResponse({
            "error_summary": {
                "total_errors": len(error_logs),
                "unique_error_types": len(error_groups),
                "period_hours": hours
            },
            "error_groups": error_groups,
            "timestamp": datetime.now().isoformat()
        })
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка получения ошибок: {str(e)}")

@router.get("/google-sheets/performance")
async def get_performance_metrics(
    hours: int = Query(24, ge=1, le=168, description="Период для анализа производительности")
):
    """
    Получить метрики производительности операций
    """
    try:
        since = datetime.now() - timedelta(hours=hours)
        logs = await google_sheets_monitor.get_recent_logs(limit=1000, since=since)
        
        # Группируем по типам операций
        performance_by_operation = {}
        
        for log in logs:
            if log.duration_ms is None:
                continue
                
            op_type = log.operation_type.value
            
            if op_type not in performance_by_operation:
                performance_by_operation[op_type] = {
                    "durations": [],
                    "success_count": 0,
                    "error_count": 0
                }
            
            performance_by_operation[op_type]["durations"].append(log.duration_ms)
            
            if log.status == OperationStatus.SUCCESS:
                performance_by_operation[op_type]["success_count"] += 1
            else:
                performance_by_operation[op_type]["error_count"] += 1
        
        # Рассчитываем статистики
        metrics = {}
        for op_type, data in performance_by_operation.items():
            durations = data["durations"]
            if durations:
                durations.sort()
                n = len(durations)
                
                metrics[op_type] = {
                    "total_operations": n,
                    "success_rate": data["success_count"] / (data["success_count"] + data["error_count"]) * 100,
                    "avg_duration_ms": sum(durations) / n,
                    "min_duration_ms": min(durations),
                    "max_duration_ms": max(durations),
                    "median_duration_ms": durations[n // 2],
                    "p95_duration_ms": durations[int(n * 0.95)] if n > 0 else 0,
                    "p99_duration_ms": durations[int(n * 0.99)] if n > 0 else 0
                }
        
        return JSONResponse({
            "period_hours": hours,
            "performance_metrics": metrics,
            "timestamp": datetime.now().isoformat()
        })
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка получения метрик производительности: {str(e)}")

@router.delete("/google-sheets/logs")
async def clear_old_logs(
    days: int = Query(7, ge=1, le=30, description="Удалить логи старше указанного количества дней")
):
    """
    Очистить старые логи для экономии места
    """
    try:
        cutoff_date = datetime.now() - timedelta(days=days)
        
        # В реальной реализации здесь будет логика очистки
        # Пока что возвращаем симуляцию
        
        return JSONResponse({
            "message": f"Логи старше {days} дней будут удалены",
            "cutoff_date": cutoff_date.isoformat(),
            "simulation": True,
            "timestamp": datetime.now().isoformat()
        })
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка очистки логов: {str(e)}")
