"""Centralized DRF exception handling."""
from rest_framework.views import exception_handler as drf_exception_handler
from rest_framework import status
from infrastructure.responses import ErrorResponse
from infrastructure.logging import get_logger

logger = get_logger(__name__)


def api_exception_handler(exc, context):
    """
    Centralized exception handler for all API exceptions.
    Converts DRF exceptions and custom exceptions to unified error format.
    """
    response = drf_exception_handler(exc, context)

    if response is not None:
        # Extract error info from DRF response
        error_code = getattr(exc, 'error_code', 'API_ERROR')
        errors = getattr(exc, 'errors', {})
        detail = str(exc.detail) if hasattr(exc, 'detail') else 'An error occurred'

        # Log the exception
        request = context.get('request')
        request_id = getattr(request, 'request_id', 'unknown')
        logger.warning(
            f'API Exception: {error_code}',
            extra={
                'request_id': request_id,
                'status_code': response.status_code,
                'error_code': error_code,
                'detail': detail,
                'errors': errors,
            }
        )

        # Format response
        response.data = {
            'success': False,
            'message': detail,
            'error_code': error_code,
            'errors': errors if errors else {},
        }

        return response

    # Unhandled exception
    error_code = 'INTERNAL_ERROR'
    detail = 'An internal error occurred'
    status_code = status.HTTP_500_INTERNAL_SERVER_ERROR

    request = context.get('request')
    request_id = getattr(request, 'request_id', 'unknown')

    logger.error(
        f'Unhandled Exception: {type(exc).__name__}',
        extra={
            'request_id': request_id,
            'error': str(exc),
        },
        exc_info=True
    )

    return ErrorResponse(
        message=detail,
        error_code=error_code,
        status_code=status_code,
    )
