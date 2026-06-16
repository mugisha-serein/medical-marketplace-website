"""
Development settings — local development environment.
All overrides are driven by environment variables in .env.
"""
from decouple import config
from .base import *

INSTALLED_APPS += ['django_extensions']

CELERY_TASK_EAGER_PROPAGATES = config('CELERY_TASK_EAGER_PROPAGATES', cast=bool)

INTERNAL_IPS = config('INTERNAL_IPS', cast=Csv())

print(f'Development settings loaded (DEBUG={DEBUG}, ENVIRONMENT={ENVIRONMENT})')
