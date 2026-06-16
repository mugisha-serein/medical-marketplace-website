"""
Production settings — hardened for production deployment.
All sensitive values MUST be provided via environment variables.
"""
from decouple import config, Csv
from .base import *

if DEBUG:
    raise ValueError('DEBUG must be False in production! Set DEBUG=False in .env')

if ENVIRONMENT != 'production':
    raise ValueError(
        f'ENVIRONMENT must be "production", got "{ENVIRONMENT}". '
        'Set ENVIRONMENT=production in .env'
    )

INSECURE_SECRET_KEYS = config('INSECURE_SECRET_KEYS', cast=Csv())
if SECRET_KEY in INSECURE_SECRET_KEYS:
    raise ValueError('SECRET_KEY is insecure! Generate a new SECRET_KEY and set it in .env')

SECURE_BROWSER_XSS_FILTER = config('SECURE_BROWSER_XSS_FILTER', cast=bool)
SECURE_CONTENT_TYPE_NOSNIFF = config('SECURE_CONTENT_TYPE_NOSNIFF', cast=bool)

if not USE_S3:
    raise ValueError('USE_S3 must be True in production! Set USE_S3=True in .env')

if CELERY_TASK_ALWAYS_EAGER:
    raise ValueError(
        'CELERY_TASK_ALWAYS_EAGER must be False in production! '
        'Set CELERY_TASK_ALWAYS_EAGER=False in .env'
    )

if not SENTRY_DSN:
    print('WARNING: SENTRY_DSN not configured. Error tracking is disabled.')

print(f'Production settings loaded (ENVIRONMENT={ENVIRONMENT}, DEBUG={DEBUG})')
print(f'SSL redirect: {SECURE_SSL_REDIRECT}')
print(f'HSTS enabled: {SECURE_HSTS_SECONDS}s')
print(f'S3 storage: {AWS_STORAGE_BUCKET_NAME}')
