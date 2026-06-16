"""Inventory selectors for optimized stock queries."""
from typing import QuerySet
from infrastructure.selectors import BaseSelector
from apps.inventory.models import StockRecord, StockMovement


class StockRecordSelector(BaseSelector):
    """Optimized queries for StockRecord model."""
    
    model = StockRecord
    
    @classmethod
    def get_queryset(cls) -> QuerySet:
        """Get stock records with product data."""
        return super().get_queryset().select_related('product')
    
    @classmethod
    def get_low_stock_items(cls) -> QuerySet:
        """Get items with low stock."""
        return cls.get_queryset().filter(quantity__lte=5)
    
    @classmethod
    def get_out_of_stock_items(cls) -> QuerySet:
        """Get out of stock items."""
        return cls.get_queryset().filter(quantity=0)


class StockMovementSelector(BaseSelector):
    """Optimized queries for StockMovement model (audit log)."""
    
    model = StockMovement
    
    @classmethod
    def get_queryset(self) -> QuerySet:
        """Get movements with related stock record."""
        return super().get_queryset().select_related('stock_record')
    
    @classmethod
    def get_movements_for_product(cls, product_id: str) -> QuerySet:
        """Get all stock movements for a product."""
        return cls.get_queryset().filter(
            stock_record__product_id=product_id
        ).order_by('-created_at')


__all__ = ['StockRecordSelector', 'StockMovementSelector']
