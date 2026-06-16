from django.urls import path
from django.http import JsonResponse
from django.db import connection
from django.core.cache import cache
from infrastructure.responses import SuccessResponse, ErrorResponse
from rest_framework import status
import time


def health_check(request):
    """Liveness probe: is the service responding?"""
    checks = {}
    response_status = status.HTTP_200_OK

    # Database check
    try:
        start = time.monotonic()
        with connection.cursor() as cursor:
            cursor.execute('SELECT 1')
        checks['database'] = {'status': 'ok', 'latency_ms': round((time.monotonic() - start) * 1000, 2)}
    except Exception as e:
        checks['database'] = {'status': 'error', 'error': str(e)}
        response_status = status.HTTP_503_SERVICE_UNAVAILABLE

    # Cache (Redis) check
    try:
        start = time.monotonic()
        cache.set('health_check', 'ok', 5)
        val = cache.get('health_check')
        checks['cache'] = {
            'status': 'ok' if val == 'ok' else 'degraded',
            'latency_ms': round((time.monotonic() - start) * 1000, 2),
        }
    except Exception as e:
        checks['cache'] = {'status': 'warning', 'error': str(e)}

    response = SuccessResponse(
        data=checks,
        message='Health check complete',
        status_code=response_status
    )
    response.status_code = response_status
    return response


def readiness_check(request):
    """Readiness probe: is the service ready to serve traffic?"""
    checks = {}
    all_ready = True

    # Database connectivity
    try:
        with connection.cursor() as cursor:
            cursor.execute('SELECT 1')
        checks['database'] = 'ready'
    except Exception as e:
        checks['database'] = f'not ready: {str(e)}'
        all_ready = False

    # Cache connectivity
    try:
        cache.set('readiness_check', 'ok', 5)
        checks['cache'] = 'ready'
    except Exception as e:
        checks['cache'] = f'not ready: {str(e)}'
        all_ready = False

    response_status = status.HTTP_200_OK if all_ready else status.HTTP_503_SERVICE_UNAVAILABLE

    response = SuccessResponse(
        data=checks,
        message='Readiness check complete',
        status_code=response_status
    )
    response.status_code = response_status
    return response


urlpatterns = [
    path('', health_check, name='health-check'),
    path('live/', health_check, name='health_check'),
    path('ready/', readiness_check, name='readiness_check'),
]
