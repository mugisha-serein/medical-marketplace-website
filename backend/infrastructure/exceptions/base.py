"""Custom exception classes for enterprise API."""
from rest_framework.exceptions import APIException as DRFAPIException
from rest_framework import status


class APIException(DRFAPIException):
    """Base exception for all API errors."""
    status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
    default_code = 'INTERNAL_ERROR'
    default_detail = 'An error occurred'

    def __init__(self, detail=None, code=None, error_code=None, errors=None):
        self.error_code = error_code or self.default_code
        self.errors = errors or {}
        super().__init__(detail=detail or self.default_detail, code=code or self.default_code)


class ValidationError(APIException):
    """Raised when request data fails validation."""
    status_code = status.HTTP_400_BAD_REQUEST
    default_code = 'VALIDATION_ERROR'
    default_detail = 'Validation error'

    def __init__(self, detail=None, errors=None, **kwargs):
        super().__init__(detail=detail, error_code='VALIDATION_ERROR', errors=errors, **kwargs)


class AuthenticationError(APIException):
    """Raised when authentication fails."""
    status_code = status.HTTP_401_UNAUTHORIZED
    default_code = 'AUTHENTICATION_ERROR'
    default_detail = 'Authentication failed'

    def __init__(self, detail=None, **kwargs):
        super().__init__(detail=detail, error_code='AUTHENTICATION_ERROR', **kwargs)


class AuthorizationError(APIException):
    """Raised when user lacks permission for action."""
    status_code = status.HTTP_403_FORBIDDEN
    default_code = 'AUTHORIZATION_ERROR'
    default_detail = 'Permission denied'

    def __init__(self, detail=None, **kwargs):
        super().__init__(detail=detail, error_code='AUTHORIZATION_ERROR', **kwargs)


class NotFoundError(APIException):
    """Raised when resource not found."""
    status_code = status.HTTP_404_NOT_FOUND
    default_code = 'NOT_FOUND'
    default_detail = 'Resource not found'

    def __init__(self, detail=None, **kwargs):
        super().__init__(detail=detail, error_code='NOT_FOUND', **kwargs)


class ConflictError(APIException):
    """Raised on state/constraint conflicts."""
    status_code = status.HTTP_409_CONFLICT
    default_code = 'CONFLICT'
    default_detail = 'Resource conflict'

    def __init__(self, detail=None, **kwargs):
        super().__init__(detail=detail, error_code='CONFLICT', **kwargs)


class RateLimitError(APIException):
    """Raised when rate limit exceeded."""
    status_code = status.HTTP_429_TOO_MANY_REQUESTS
    default_code = 'RATE_LIMITED'
    default_detail = 'Rate limit exceeded'

    def __init__(self, detail=None, **kwargs):
        super().__init__(detail=detail, error_code='RATE_LIMITED', **kwargs)


class TransactionError(APIException):
    """Raised on transaction/database errors."""
    status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
    default_code = 'TRANSACTION_ERROR'
    default_detail = 'Transaction error'

    def __init__(self, detail=None, **kwargs):
        super().__init__(detail=detail, error_code='TRANSACTION_ERROR', **kwargs)


class InventoryError(APIException):
    """Raised on inventory/stock operation failures."""
    status_code = status.HTTP_400_BAD_REQUEST
    default_code = 'INVENTORY_ERROR'
    default_detail = 'Inventory operation failed'

    def __init__(self, detail=None, **kwargs):
        super().__init__(detail=detail, error_code='INVENTORY_ERROR', **kwargs)
