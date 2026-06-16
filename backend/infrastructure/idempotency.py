"""Idempotency utilities for critical write operations."""
import hashlib
import json
from typing import Any, Callable
from infrastructure.cache import CacheManager
from infrastructure.exceptions import ConflictError
from infrastructure.logging import get_logger

logger = get_logger(__name__)


class IdempotencyManager:
    """
    Manages idempotent operations for critical writes.
    
    Rules:
    - Same request (same idempotency key) returns cached result
    - Prevents duplicate operations in case of retries
    - Used for checkout, order creation, etc.
    """
    
    @staticmethod
    def generate_key(user_id: str, operation: str, params: dict) -> str:
        """Generate deterministic idempotency key from params."""
        param_json = json.dumps(params, sort_keys=True, default=str)
        hash_digest = hashlib.sha256(param_json.encode()).hexdigest()
        return f'idempotency:{user_id}:{operation}:{hash_digest}'
    
    @staticmethod
    def execute_once(user_id: str, operation: str, params: dict, func: Callable, timeout: int = 3600) -> Any:
        """
        Execute function only once per idempotency key.
        Returns cached result if already executed.
        """
        idempotency_key = IdempotencyManager.generate_key(user_id, operation, params)
        
        # Check if already executed
        cached_result = CacheManager.get(idempotency_key)
        if cached_result is not None:
            logger.info(
                f'Idempotent operation cached: {operation}',
                extra={'idempotency_key': idempotency_key}
            )
            return cached_result
        
        # Execute function
        try:
            result = func()
            # Cache result
            CacheManager.set(idempotency_key, result, timeout)
            logger.info(
                f'Idempotent operation executed: {operation}',
                extra={'idempotency_key': idempotency_key}
            )
            return result
        except Exception as e:
            logger.error(
                f'Idempotent operation failed: {operation}',
                extra={'idempotency_key': idempotency_key, 'error': str(e)},
                exc_info=True
            )
            raise


__all__ = ['IdempotencyManager']
