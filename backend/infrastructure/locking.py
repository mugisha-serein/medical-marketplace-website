"""Distributed locking for concurrency control."""
import time
import uuid
from typing import Optional
from django.core.cache import cache
from infrastructure.logging import get_logger

logger = get_logger(__name__)


class DistributedLock:
    """
    Redis-backed distributed lock for concurrency-critical operations.
    
    Rules:
    - Used for stock mutations to prevent race conditions
    - Auto-release after timeout
    - Prevents oversell scenarios
    """
    
    def __init__(self, key: str, timeout: int = 30, max_retries: int = 5):
        self.key = f'lock:{key}'
        self.timeout = timeout
        self.max_retries = max_retries
        self.lock_id = str(uuid.uuid4())
        self.acquired = False
    
    def acquire(self) -> bool:
        """Try to acquire the lock."""
        for attempt in range(self.max_retries):
            # Use Redis SET NX (set if not exists)
            try:
                if cache.add(self.key, self.lock_id, self.timeout):
                    self.acquired = True
                    logger.debug(
                        f'Lock acquired: {self.key}',
                        extra={'lock_id': self.lock_id, 'attempt': attempt + 1}
                    )
                    return True
            except Exception as e:
                logger.warning(f'Lock acquisition error: {str(e)}')
            
            if attempt < self.max_retries - 1:
                time.sleep(0.1 * (attempt + 1))  # Exponential backoff
        
        logger.warning(
            f'Lock acquisition failed after {self.max_retries} attempts: {self.key}',
            extra={'lock_id': self.lock_id}
        )
        return False
    
    def release(self) -> bool:
        """Release the lock if we own it."""
        if not self.acquired:
            return False
        
        try:
            # Only delete if we own the lock
            current_value = cache.get(self.key)
            if current_value == self.lock_id:
                cache.delete(self.key)
                self.acquired = False
                logger.debug(f'Lock released: {self.key}')
                return True
        except Exception as e:
            logger.warning(f'Lock release error: {str(e)}')
        
        return False
    
    def __enter__(self):
        if not self.acquire():
            raise RuntimeError(f'Failed to acquire lock: {self.key}')
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.release()


__all__ = ['DistributedLock']
