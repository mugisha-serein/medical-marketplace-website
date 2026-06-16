"""Base service class for business logic."""
from django.db import transaction
from infrastructure.logging import get_logger

logger = get_logger(__name__)


class BaseService:
    """
    Base service class for encapsulating business logic.
    
    Rules:
    - All state mutations must pass through services
    - Services manage transactions
    - Services coordinate across models
    - Services validate business rules
    - Services log state changes
    """
    
    @staticmethod
    @transaction.atomic
    def execute(func, *args, **kwargs):
        """Execute a service operation within a transaction."""
        return func(*args, **kwargs)
    
    @staticmethod
    def log_action(action, entity_type, entity_id, **metadata):
        """Log business action for audit trail."""
        logger.info(
            f'Action: {action} {entity_type}',
            extra={
                'action': action,
                'entity_type': entity_type,
                'entity_id': entity_id,
                **metadata,
            }
        )


__all__ = ['BaseService']
