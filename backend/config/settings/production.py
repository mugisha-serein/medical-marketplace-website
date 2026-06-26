"""Production-style settings for the SQLite presentation MVP.

This file intentionally stays aligned with `base.py`: SQLite database,
local/static media, locmem cache, and no PostgreSQL, Redis, Celery, S3,
or python-decouple dependency.
"""
import os

from .base import *  # noqa: F403,F401

DEBUG = False
ENVIRONMENT = os.getenv('ENVIRONMENT', 'production')

# Keep the same comma-separated format as base.py so deployment remains simple.
ALLOWED_HOSTS = [
    host.strip()
    for host in os.getenv('ALLOWED_HOSTS', 'localhost,127.0.0.1').split(',')
    if host.strip()
]

CORS_ALLOWED_ORIGINS = [
    origin.strip()
    for origin in os.getenv('CORS_ALLOWED_ORIGINS', '').split(',')
    if origin.strip()
]
CSRF_TRUSTED_ORIGINS = [
    origin.strip()
    for origin in os.getenv('CSRF_TRUSTED_ORIGINS', ','.join(CORS_ALLOWED_ORIGINS)).split(',')
    if origin.strip()
]

# Safe Django production toggles that do not require extra services.
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_REFERRER_POLICY = 'same-origin'
X_FRAME_OPTIONS = 'DENY'

# Enable these by env only when the app is deployed behind HTTPS.
SECURE_SSL_REDIRECT = os.getenv('SECURE_SSL_REDIRECT', 'false').lower() in {'1', 'true', 'yes', 'on'}
SESSION_COOKIE_SECURE = SECURE_SSL_REDIRECT
CSRF_COOKIE_SECURE = SECURE_SSL_REDIRECT

print(f'SQLite MVP production settings loaded (ENVIRONMENT={ENVIRONMENT}, DEBUG={DEBUG})')
print(f'Database engine: {DATABASES["default"]["ENGINE"]}')  # noqa: F405
print(f'Allowed hosts: {ALLOWED_HOSTS}')
