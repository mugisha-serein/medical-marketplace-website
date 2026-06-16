"""Request ID / Correlation ID middleware."""
import uuid


class CorrelationIDMiddleware:
    """Add unique request ID for tracing requests across logs."""
    
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Generate or extract request ID
        request_id = (
            request.META.get('HTTP_X_REQUEST_ID') or
            request.META.get('HTTP_X_CORRELATION_ID') or
            str(uuid.uuid4())
        )
        
        request.request_id = request_id
        request.META['HTTP_X_REQUEST_ID'] = request_id

        response = self.get_response(request)
        response['X-Request-ID'] = request_id
        
        return response


__all__ = ['CorrelationIDMiddleware']
