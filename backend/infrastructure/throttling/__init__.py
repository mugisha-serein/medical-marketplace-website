"""Rate limiting and throttling."""
from rest_framework.throttling import UserRateThrottle, AnonRateThrottle


class StandardUserThrottle(UserRateThrottle):
    """Standard rate limit: 1000 requests per hour per user."""
    scope = 'standard_user'
    rate = '1000/hour'


class StandardAnonThrottle(AnonRateThrottle):
    """Standard rate limit: 100 requests per hour for anonymous users."""
    scope = 'standard_anon'
    rate = '100/hour'


class StrictUserThrottle(UserRateThrottle):
    """Strict rate limit: 100 requests per hour per user."""
    scope = 'strict_user'
    rate = '100/hour'


class WriteOperationThrottle(UserRateThrottle):
    """Strict rate limit for write operations: 50 per hour."""
    scope = 'write_operation'
    rate = '50/hour'


__all__ = [
    'StandardUserThrottle',
    'StandardAnonThrottle',
    'StrictUserThrottle',
    'WriteOperationThrottle',
]
