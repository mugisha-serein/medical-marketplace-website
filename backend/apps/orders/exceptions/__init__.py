"""Order-specific exceptions."""
from infrastructure.exceptions import APIException
from rest_framework import status


class OrderCreationError(APIException):
    """Raised when order creation fails."""
    status_code = status.HTTP_400_BAD_REQUEST
    default_code = 'ORDER_CREATION_ERROR'
    default_detail = 'Failed to create order'


class InvalidStatusTransitionError(APIException):
    """Raised on invalid order status transition."""
    status_code = status.HTTP_400_BAD_REQUEST
    default_code = 'INVALID_STATUS_TRANSITION'
    default_detail = 'Invalid order status transition'


class OrderNotFoundError(APIException):
    """Raised when order not found."""
    status_code = status.HTTP_404_NOT_FOUND
    default_code = 'ORDER_NOT_FOUND'
    default_detail = 'Order not found'


__all__ = ['OrderCreationError', 'InvalidStatusTransitionError', 'OrderNotFoundError']
