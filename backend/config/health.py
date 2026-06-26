from django.urls import path
from django.http import JsonResponse
from django.db import connection
from django.core.cache import cache
from rest_framework import status
import time


def _json_response(data, message, status_code):
    return JsonResponse(
        {'success': status_code < 400, 'message': message, 'data': data},
        status=status_code,
    )


def health_check(request):
    checks = {}
    response_status = status.HTTP_200_OK

    try:
        start = time.monotonic()
        with connection.cursor() as cursor:
            cursor.execute('SELECT 1')
        checks['database'] = {'status': 'ok', 'latency_ms': round((time.monotonic() - start) * 1000, 2)}
    except Exception as e:
        checks['database'] = {'status': 'error', 'error': str(e)}
        response_status = status.HTTP_503_SERVICE_UNAVAILABLE

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

    return _json_response(checks, 'Health check complete', response_status)


def readiness_check(request):
    checks = {}
    all_ready = True

    try:
        with connection.cursor() as cursor:
            cursor.execute('SELECT 1')
        checks['database'] = 'ready'
    except Exception as e:
        checks['database'] = f'not ready: {str(e)}'
        all_ready = False

    try:
        cache.set('readiness_check', 'ok', 5)
        checks['cache'] = 'ready'
    except Exception as e:
        checks['cache'] = f'not ready: {str(e)}'
        all_ready = False

    response_status = status.HTTP_200_OK if all_ready else status.HTTP_503_SERVICE_UNAVAILABLE
    return _json_response(checks, 'Readiness check complete', response_status)


urlpatterns = [
    path('', health_check, name='health-check'),
    path('live/', health_check, name='health_check'),
    path('ready/', readiness_check, name='readiness_check'),
]
