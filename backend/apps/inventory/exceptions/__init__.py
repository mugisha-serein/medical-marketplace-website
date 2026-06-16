"""Inventory-specific exceptions."""
from infrastructure.exceptions import APIException
from rest_framework import status


class InsufficientStockError(APIException):
    """Raised when insufficient stock available."""
    status_code = status.HTTP_400_BAD_REQUEST
    default_code = 'INSUFFICIENT_STOCK'
    default_detail = 'Insufficient stock'


class InvalidStockMutationError(APIException):
    """Raised on invalid stock operation."""
    status_code = status.HTTP_400_BAD_REQUEST
    default_code = 'INVALID_STOCK_MUTATION'
    default_detail = 'Invalid stock operation'


class StockLockError(APIException):
    """Raised when cannot acquire stock lock."""
    status_code = status.HTTP_409_CONFLICT
    default_code = 'STOCK_LOCK_ERROR'
    default_detail = 'Could not acquire stock lock'


__all__ = ['InsufficientStockError', 'InvalidStockMutationError', 'StockLockError']
