"""Prometheus metrics collection."""
import logging

logger = logging.getLogger(__name__)


class MetricsCollector:
    """Base metrics collector for Prometheus integration."""
    
    @staticmethod
    def record_request(method, path, status_code, duration_ms):
        """Record HTTP request metric."""
        logger.info(
            f'HTTP Request: {method} {path} {status_code}',
            extra={
                'http_method': method,
                'http_path': path,
                'http_status': status_code,
                'duration_ms': duration_ms,
            }
        )
    
    @staticmethod
    def record_database_query(query_type, table, duration_ms):
        """Record database query metric."""
        logger.debug(
            f'DB Query: {query_type} {table}',
            extra={
                'query_type': query_type,
                'table': table,
                'duration_ms': duration_ms,
            }
        )
    
    @staticmethod
    def record_cache_operation(operation, key, hit=None):
        """Record cache operation metric."""
        logger.debug(
            f'Cache {operation}: {key}',
            extra={
                'cache_operation': operation,
                'cache_key': key,
                'cache_hit': hit,
            }
        )
    
    @staticmethod
    def record_async_task(task_name, duration_ms, success=True):
        """Record Celery task execution metric."""
        logger.info(
            f'Celery Task: {task_name} ({'SUCCESS' if success else 'FAILED'})',
            extra={
                'task_name': task_name,
                'duration_ms': duration_ms,
                'task_success': success,
            }
        )


__all__ = ['MetricsCollector']
