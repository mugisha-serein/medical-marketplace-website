"""Catalog selectors for optimized queries."""
from typing import Optional, List, QuerySet
from infrastructure.selectors import BaseSelector
from apps.catalog.models import Product, Category


class ProductSelector(BaseSelector):
    """Optimized queries for Product model."""
    
    model = Product
    
    @classmethod
    def get_queryset(cls) -> QuerySet:
        """Get products with related data."""
        return super().get_queryset().select_related('vendor')
    
    @classmethod
    def get_active_products(cls) -> QuerySet:
        """Get all active products."""
        return cls.get_queryset().filter(is_active=True)
    
    @classmethod
    def search_products(cls, query: str) -> QuerySet:
        """Search products by name or description."""
        from django.db.models import Q
        return cls.get_active_products().filter(
            Q(name__icontains=query) | Q(description__icontains=query)
        )
    
    @classmethod
    def filter_by_category(cls, category_id: str) -> QuerySet:
        """Get products by category."""
        return cls.get_active_products().filter(category_id=category_id)


class CategorySelector(BaseSelector):
    """Optimized queries for Category model."""
    
    model = Category
    
    @classmethod
    def get_active_categories(cls) -> QuerySet:
        """Get all active categories."""
        return cls.get_queryset().filter(is_active=True)


__all__ = ['ProductSelector', 'CategorySelector']
