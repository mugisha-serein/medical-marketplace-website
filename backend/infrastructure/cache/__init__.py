"""Redis cache management."""
from django.core.cache import cache
from typing import Any, Optional
import json
from infrastructure.logging import get_logger
from infrastructure.metrics import MetricsCollector

logger = get_logger(__name__)


class CacheManager:
    """Centralized Redis cache management."""
    
    @staticmethod
    def get(key: str, default: Any = None) -> Any:
        """Get value from cache."""
        try:
            value = cache.get(key)
            MetricsCollector.record_cache_operation('GET', key, hit=value is not None)
            return value if value is not None else default
        except Exception as e:
            logger.warning(f'Cache GET failed: {key}', extra={'error': str(e)})
            return default
    
    @staticmethod
    def set(key: str, value: Any, timeout: int = 3600) -> bool:
        """Set value in cache."""
        try:
            cache.set(key, value, timeout)
            MetricsCollector.record_cache_operation('SET', key)
            return True
        except Exception as e:
            logger.warning(f'Cache SET failed: {key}', extra={'error': str(e)})
            return False
    
    @staticmethod
    def delete(key: str) -> bool:
        """Delete key from cache."""
        try:
            cache.delete(key)
            MetricsCollector.record_cache_operation('DELETE', key)
            return True
        except Exception as e:
            logger.warning(f'Cache DELETE failed: {key}', extra={'error': str(e)})
            return False
    
    @staticmethod
    def clear_pattern(pattern: str) -> int:
        """Clear all keys matching pattern."""
        try:
            # Redis-specific: use cache client directly
            client = cache.client
            keys = client.keys(pattern)
            if keys:
                client.delete(*keys)
            logger.info(f'Cleared cache pattern: {pattern}', extra={'keys_deleted': len(keys)})
            return len(keys)
        except Exception as e:
            logger.warning(f'Cache pattern clear failed: {pattern}', extra={'error': str(e)})
            return 0
    
    @staticmethod
    def increment(key: str, delta: int = 1, timeout: int = 3600) -> int:
        """Increment numeric value in cache."""
        try:
            return cache.incr(key, delta)
        except Exception:
            # Key doesn't exist, set initial value
            cache.set(key, delta, timeout)
            return delta
    
    @staticmethod
    def decrement(key: str, delta: int = 1) -> int:
        """Decrement numeric value in cache."""
        try:
            return cache.decr(key, delta)
        except Exception:
            return 0


__all__ = ['CacheManager']
