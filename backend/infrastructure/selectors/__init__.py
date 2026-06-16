"""Base selector/query class for optimized reads."""
from typing import Optional, List, Dict, Any
from django.db.models import QuerySet, Model
from infrastructure.logging import get_logger

logger = get_logger(__name__)


class BaseSelector:
    """
    Base selector class for read operations.
    
    Rules:
    - Selectors handle all complex queries
    - Selectors optimize with select_related/prefetch_related
    - Selectors never modify state
    - Selectors can use caching
    - Selectors coordinate across models for reads
    """
    
    model: Optional[type[Model]] = None
    
    @classmethod
    def get_queryset(cls) -> QuerySet:
        """Get base queryset for this selector."""
        if cls.model is None:
            raise NotImplementedError('model attribute must be set')
        return cls.model.objects.all()
    
    @classmethod
    def get_by_id(cls, id: Any) -> Optional[Model]:
        """Get single object by ID."""
        try:
            return cls.get_queryset().get(id=id)
        except cls.model.DoesNotExist:
            return None
    
    @classmethod
    def filter(cls, **filters) -> QuerySet:
        """Filter queryset."""
        return cls.get_queryset().filter(**filters)
    
    @classmethod
    def list_all(cls, limit: Optional[int] = None) -> QuerySet:
        """Get all objects, optionally limited."""
        queryset = cls.get_queryset()
        if limit:
            queryset = queryset[:limit]
        return queryset
    
    @classmethod
    def exists(cls, **filters) -> bool:
        """Check if object exists."""
        return cls.get_queryset().filter(**filters).exists()


__all__ = ['BaseSelector']
