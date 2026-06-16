"""Cart-specific exceptions."""
from infrastructure.exceptions import APIException
from rest_framework import status


class CartValidationError(APIException):
    """Raised when cart validation fails."""
    status_code = status.HTTP_400_BAD_REQUEST
    default_code = 'CART_VALIDATION_ERROR'
    default_detail = 'Cart validation failed'


class EmptyCartError(APIException):
    """Raised when cart is empty."""
    status_code = status.HTTP_400_BAD_REQUEST
    default_code = 'EMPTY_CART'
    default_detail = 'Cart is empty'


class InvalidCartItemError(APIException):
    """Raised when cart item is invalid."""
    status_code = status.HTTP_400_BAD_REQUEST
    default_code = 'INVALID_CART_ITEM'
    default_detail = 'Invalid cart item'


__all__ = ['CartValidationError', 'EmptyCartError', 'InvalidCartItemError']
