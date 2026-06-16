"""
Base settings — shared across all environments.
ALL secrets and environment-specific values MUST be loaded from environment variables.
NO hardcoded secrets, URLs, credentials, or ports.
"""
from pathlib import Path
from datetime import timedelta
from decouple import config, Csv, UndefinedValueError

import dj_database_url

BASE_DIR = Path(__file__).resolve().parent.parent.parent


def env_first(*keys, default=None, cast=None):
    """Return the first non-empty environment variable among *keys."""
    for key in keys:
        value = config(key, default=None)
        if value is not None and value != '':
            if cast is not None:
                return cast(value)
            return value
    if default is not None:
        if cast is not None:
            return cast(default)
        return default
    raise UndefinedValueError(
        f'None of {", ".join(keys)} found. Declare one in .env.'
    )


# ── Required Environment Variables ───────────────────────────────────────────
SECRET_KEY = config('SECRET_KEY')
DEBUG = config('DEBUG', cast=bool)
ENVIRONMENT = config('ENVIRONMENT')

TIME_ZONE = config('TIME_ZONE')
LANGUAGE_CODE = config('LANGUAGE_CODE')
USE_I18N = config('USE_I18N', cast=bool)
USE_TZ = config('USE_TZ', cast=bool)

# ── Application Info ────────────────────────────────────────────────────────
APP_NAME = config('APP_NAME')
APP_VERSION = config('APP_VERSION')
API_VERSION = config('API_VERSION')

# ── Hosts & CORS ────────────────────────────────────────────────────────────
ALLOWED_HOSTS = config('ALLOWED_HOSTS', cast=Csv())
CSRF_TRUSTED_ORIGINS = config('CSRF_TRUSTED_ORIGINS', cast=Csv())

# ── Frontend Integration ──────────────────────────────────────────────────────
FRONTEND_URL = config('FRONTEND_URL')
FRONTEND_ADMIN_URL = config('FRONTEND_ADMIN_URL')
PUBLIC_API_URL = config('PUBLIC_API_URL')

# ── Installed Apps ──────────────────────────────────────────────────────────
DJANGO_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.postgres',
]

THIRD_PARTY_APPS = [
    'rest_framework',
    'rest_framework_simplejwt',
    'rest_framework_simplejwt.token_blacklist',
    'corsheaders',
    'django_filters',
    'drf_spectacular',
    'axes',
    'django_celery_beat',
    'django_celery_results',
]

LOCAL_APPS = [
    'apps.accounts',
    'apps.catalog',
    'apps.cart',
    'apps.orders',
    'apps.inventory',
    'apps.kpi',
    'apps.inquiries',
    'apps.notification',
]

INSTALLED_APPS = DJANGO_APPS + THIRD_PARTY_APPS + LOCAL_APPS

# ── Middleware ───────────────────────────────────────────────────────────────
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'axes.middleware.AxesMiddleware',
]

ROOT_URLCONF = 'config.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'config.wsgi.application'

# ── Database ─────────────────────────────────────────────────────────────────
DATABASE_URL = config('DATABASE_URL', default=None)

if DATABASE_URL:
    import dj_database_url

    DATABASES = {
        'default': dj_database_url.config(
            default=DATABASE_URL,
            conn_max_age=config('DB_CONN_MAX_AGE', cast=int),
        )
    }
else:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql',
            'NAME': env_first('POSTGRES_DB', 'DB_NAME'),
            'USER': env_first('POSTGRES_USER', 'DB_USER'),
            'PASSWORD': env_first('POSTGRES_PASSWORD', 'DB_PASSWORD'),
            'HOST': env_first('POSTGRES_HOST', 'DB_HOST'),
            'PORT': env_first('POSTGRES_PORT', 'DB_PORT', cast=int),
            'CONN_MAX_AGE': config('DB_CONN_MAX_AGE', cast=int),
            'CONNECT_TIMEOUT': config('DB_CONNECT_TIMEOUT', cast=int),
            'OPTIONS': {
                'sslmode': config('DB_SSL_MODE'),
            },
        }
    }

# ── Redis Configuration ────────────────────────────────────────────────────────
REDIS_URL = config('REDIS_URL')
REDIS_CACHE_DB = config('REDIS_CACHE_DB', cast=int)
REDIS_SESSION_DB = config('REDIS_SESSION_DB', cast=int)
REDIS_KPI_DB = config('REDIS_KPI_DB', cast=int)
REDIS_LOCK_DB = config('REDIS_LOCK_DB', cast=int)
REDIS_SOCKET_CONNECT_TIMEOUT = config('REDIS_SOCKET_CONNECT_TIMEOUT', cast=int)
REDIS_SOCKET_TIMEOUT = config('REDIS_SOCKET_TIMEOUT', cast=int)

# ── Cache (Redis) ─────────────────────────────────────────────────────────────
CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': REDIS_URL,
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
            'SOCKET_CONNECT_TIMEOUT': REDIS_SOCKET_CONNECT_TIMEOUT,
            'SOCKET_TIMEOUT': REDIS_SOCKET_TIMEOUT,
            'IGNORE_EXCEPTIONS': True,
            'DB': REDIS_CACHE_DB,
        },
        'KEY_PREFIX': config('CACHE_KEY_PREFIX'),
    }
}

SESSION_ENGINE = 'django.contrib.sessions.backends.cache'
SESSION_CACHE_ALIAS = 'default'

# ── Auth ──────────────────────────────────────────────────────────────────────
AUTH_USER_MODEL = 'accounts.User'

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
        'OPTIONS': {'min_length': config('AUTH_PASSWORD_MIN_LENGTH', cast=int)},
    },
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

AUTHENTICATION_BACKENDS = [
    'axes.backends.AxesStandaloneBackend',
    'django.contrib.auth.backends.ModelBackend',
]

# ── DRF Configuration ──────────────────────────────────────────────────────────
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
    'DEFAULT_FILTER_BACKENDS': [
        'django_filters.rest_framework.DjangoFilterBackend',
        'rest_framework.filters.SearchFilter',
        'rest_framework.filters.OrderingFilter',
    ],
    'DEFAULT_PAGINATION_CLASS': 'config.permission.CursorPagination',
    'PAGE_SIZE': config('API_PAGE_SIZE', cast=int),
    'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',
    'DEFAULT_THROTTLE_CLASSES': [
        'rest_framework.throttling.AnonRateThrottle',
        'rest_framework.throttling.UserRateThrottle',
    ],
    'DEFAULT_THROTTLE_RATES': {
        'anon': config('THROTTLE_ANON_RATE'),
        'user': config('THROTTLE_USER_RATE'),
    },
    'EXCEPTION_HANDLER': 'config.permission.custom_exception_handler',
}

# ── JWT Authentication ────────────────────────────────────────────────────────
JWT_ACCESS_MINUTES = config('JWT_ACCESS_MINUTES', cast=int)
JWT_REFRESH_DAYS = config('JWT_REFRESH_DAYS', cast=int)
JWT_ROTATE_REFRESH_TOKENS = config('JWT_ROTATE_REFRESH_TOKENS', cast=bool)
JWT_BLACKLIST_AFTER_ROTATION = config('JWT_BLACKLIST_AFTER_ROTATION', cast=bool)
JWT_ALGORITHM = config('JWT_ALGORITHM')
JWT_UPDATE_LAST_LOGIN = config('JWT_UPDATE_LAST_LOGIN', cast=bool)

SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=JWT_ACCESS_MINUTES),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=JWT_REFRESH_DAYS),
    'ROTATE_REFRESH_TOKENS': JWT_ROTATE_REFRESH_TOKENS,
    'BLACKLIST_AFTER_ROTATION': JWT_BLACKLIST_AFTER_ROTATION,
    'UPDATE_LAST_LOGIN': JWT_UPDATE_LAST_LOGIN,
    'ALGORITHM': JWT_ALGORITHM,
    'SIGNING_KEY': SECRET_KEY,
    'AUTH_HEADER_TYPES': ('Bearer',),
    'AUTH_HEADER_NAME': 'HTTP_AUTHORIZATION',
    'USER_ID_FIELD': 'id',
    'USER_ID_CLAIM': 'user_id',
    'TOKEN_OBTAIN_SERIALIZER': 'rest_framework_simplejwt.serializers.TokenObtainPairSerializer',
}

# ── Celery ─────────────────────────────────────────────────────────────────────
CELERY_BROKER_URL = config('CELERY_BROKER_URL')
CELERY_RESULT_BACKEND = config('CELERY_RESULT_BACKEND')
CELERY_ACCEPT_CONTENT = config('CELERY_ACCEPT_CONTENT', cast=Csv())
CELERY_TASK_SERIALIZER = config('CELERY_TASK_SERIALIZER')
CELERY_RESULT_SERIALIZER = config('CELERY_RESULT_SERIALIZER')
CELERY_TIMEZONE = config('CELERY_TIMEZONE')
CELERY_TASK_TRACK_STARTED = config('CELERY_TASK_TRACK_STARTED', cast=bool)
CELERY_TASK_ACKS_LATE = config('CELERY_TASK_ACKS_LATE', cast=bool)
CELERY_WORKER_PREFETCH_MULTIPLIER = config('CELERY_WORKER_PREFETCH_MULTIPLIER', cast=int)
CELERY_TASK_SOFT_TIME_LIMIT = config('CELERY_TASK_SOFT_TIME_LIMIT', cast=int)
CELERY_TASK_TIME_LIMIT = config('CELERY_TASK_TIME_LIMIT', cast=int)
CELERY_TASK_MAX_RETRIES = config('CELERY_TASK_MAX_RETRIES', cast=int)
CELERY_BEAT_SCHEDULER = config('CELERY_BEAT_SCHEDULER')
CELERY_TASK_ALWAYS_EAGER = config('CELERY_TASK_ALWAYS_EAGER', cast=bool)

# ── Axes (Brute-force Protection) ────────────────────────────────────────────
AXES_ENABLED = config('AXES_ENABLED', cast=bool)
AXES_FAILURE_LIMIT = config('AXES_FAILURE_LIMIT', cast=int)
AXES_COOLOFF_TIME = timedelta(minutes=config('AXES_COOLOFF_MINUTES', cast=int))
AXES_LOCKOUT_CALLABLE = config('AXES_LOCKOUT_CALLABLE')
AXES_RESET_ON_SUCCESS = config('AXES_RESET_ON_SUCCESS', cast=bool)
AXES_ENABLE_ACCESS_FAILURE_LOG = config('AXES_ENABLE_ACCESS_FAILURE_LOG', cast=bool)

# ── CORS ────────────────────────────────────────────────────────────────────────
CORS_ALLOWED_ORIGINS = config('CORS_ALLOWED_ORIGINS', cast=Csv())
CORS_ALLOW_CREDENTIALS = config('CORS_ALLOW_CREDENTIALS', cast=bool)
CORS_ALLOW_ALL_ORIGINS = config('CORS_ALLOW_ALL_ORIGINS', cast=bool)

# ── Email Configuration ─────────────────────────────────────────────────────────
EMAIL_BACKEND = config('EMAIL_BACKEND')
EMAIL_HOST = config('EMAIL_HOST')
EMAIL_PORT = config('EMAIL_PORT', cast=int)
EMAIL_HOST_USER = config('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = config('EMAIL_HOST_PASSWORD')
EMAIL_USE_TLS = config('EMAIL_USE_TLS', cast=bool)
DEFAULT_FROM_EMAIL = config('DEFAULT_FROM_EMAIL')
SERVER_EMAIL = config('SERVER_EMAIL')

# ── File Storage ────────────────────────────────────────────────────────────────
USE_S3 = config('USE_S3', cast=bool)
MEDIA_URL = config('MEDIA_URL')

if USE_S3:
    AWS_ACCESS_KEY_ID = config('AWS_ACCESS_KEY_ID')
    AWS_SECRET_ACCESS_KEY = config('AWS_SECRET_ACCESS_KEY')
    AWS_STORAGE_BUCKET_NAME = config('AWS_STORAGE_BUCKET_NAME')
    AWS_S3_REGION_NAME = config('AWS_S3_REGION_NAME')
    AWS_S3_CUSTOM_DOMAIN = config('AWS_S3_CUSTOM_DOMAIN', default=None)
    AWS_S3_OBJECT_PARAMETERS = {'CacheControl': config('AWS_S3_CACHE_CONTROL')}
    AWS_LOCATION = config('AWS_LOCATION')
    DEFAULT_FILE_STORAGE = config('DEFAULT_FILE_STORAGE')
    MEDIA_URL = config('AWS_MEDIA_URL')
else:
    MEDIA_ROOT = config('MEDIA_ROOT')

# ── Static Files ────────────────────────────────────────────────────────────────
STATIC_URL = config('STATIC_URL')
STATIC_ROOT = Path(config('STATIC_ROOT'))
STATICFILES_STORAGE = config('STATICFILES_STORAGE')

# ── Security Settings ───────────────────────────────────────────────────────────
SECURE_SSL_REDIRECT = config('SECURE_SSL_REDIRECT', cast=bool)
SESSION_COOKIE_SECURE = config('SESSION_COOKIE_SECURE', cast=bool)
CSRF_COOKIE_SECURE = config('CSRF_COOKIE_SECURE', cast=bool)
SECURE_HSTS_SECONDS = config('SECURE_HSTS_SECONDS', cast=int)
SECURE_HSTS_INCLUDE_SUBDOMAINS = config('SECURE_HSTS_INCLUDE_SUBDOMAINS', cast=bool)
SECURE_HSTS_PRELOAD = config('SECURE_HSTS_PRELOAD', cast=bool)
X_FRAME_OPTIONS = config('X_FRAME_OPTIONS')

# ── Logging Configuration ───────────────────────────────────────────────────────
LOG_LEVEL = config('LOG_LEVEL')
LOG_FORMAT = config('LOG_FORMAT')

if LOG_FORMAT == 'json':
    default_formatter = 'json'
else:
    default_formatter = 'verbose'

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'json': {
            '()': 'pythonjsonlogger.jsonlogger.JsonFormatter',
            'format': config('LOG_JSON_FORMAT'),
        },
        'verbose': {
            'format': config('LOG_VERBOSE_FORMAT'),
            'style': '{',
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': default_formatter,
        },
    },
    'root': {
        'handlers': ['console'],
        'level': LOG_LEVEL,
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': config('LOG_DJANGO_LEVEL'),
            'propagate': False,
        },
        'apps': {'handlers': ['console'], 'level': LOG_LEVEL, 'propagate': False},
        'celery': {'handlers': ['console'], 'level': LOG_LEVEL, 'propagate': False},
        'infrastructure': {'handlers': ['console'], 'level': LOG_LEVEL, 'propagate': False},
    },
}

# ── API Documentation ──────────────────────────────────────────────────────────
SPECTACULAR_SETTINGS = {
    'TITLE': config('API_DOCS_TITLE'),
    'DESCRIPTION': config('API_DOCS_DESCRIPTION'),
    'VERSION': API_VERSION,
    'SERVE_INCLUDE_SCHEMA': config('API_DOCS_SERVE_INCLUDE_SCHEMA', cast=bool),
    'COMPONENT_SPLIT_REQUEST': config('API_DOCS_COMPONENT_SPLIT_REQUEST', cast=bool),
}

# ── Monitoring & Observability ──────────────────────────────────────────────────
ENABLE_METRICS = config('ENABLE_METRICS', cast=bool)
ENABLE_HEALTHCHECKS = config('ENABLE_HEALTHCHECKS', cast=bool)
SENTRY_DSN = config('SENTRY_DSN', default='')
SENTRY_ENVIRONMENT = config('SENTRY_ENVIRONMENT')
SENTRY_TRACES_SAMPLE_RATE = config('SENTRY_TRACES_SAMPLE_RATE', cast=float)

if SENTRY_DSN:
    import sentry_sdk
    from sentry_sdk.integrations.django import DjangoIntegration
    from sentry_sdk.integrations.celery import CeleryIntegration

    sentry_sdk.init(
        dsn=SENTRY_DSN,
        integrations=[
            DjangoIntegration(),
            CeleryIntegration(),
        ],
        environment=SENTRY_ENVIRONMENT,
        traces_sample_rate=SENTRY_TRACES_SAMPLE_RATE,
        send_default_pii=config('SENTRY_SEND_DEFAULT_PII', cast=bool),
    )

# ── App-level Configuration ─────────────────────────────────────────────────────
KPI_CACHE_TTL = config('KPI_CACHE_TTL', cast=int)
KPI_REALTIME_ENABLED = config('KPI_REALTIME_ENABLED', cast=bool)
KPI_SNAPSHOT_CACHE_TTL = config('KPI_SNAPSHOT_CACHE_TTL', cast=int)
PRODUCT_CACHE_TTL = config('PRODUCT_CACHE_TTL', cast=int)
SEARCH_CACHE_TTL = config('SEARCH_CACHE_TTL', cast=int)

CART_TTL_DAYS = config('CART_TTL_DAYS', cast=int)
CART_MAX_ITEMS = config('CART_MAX_ITEMS', cast=int)
CART_TTL_SECONDS = CART_TTL_DAYS * 86400

ORDER_NUMBER_PREFIX = config('ORDER_NUMBER_PREFIX')
ORDER_CANCELLATION_WINDOW_MINUTES = config('ORDER_CANCELLATION_WINDOW_MINUTES', cast=int)

LOW_STOCK_THRESHOLD = config('LOW_STOCK_THRESHOLD', cast=int)
LOCK_TIMEOUT_SECONDS = config('LOCK_TIMEOUT_SECONDS', cast=int)
INVENTORY_RECONCILIATION_INTERVAL = config('INVENTORY_RECONCILIATION_INTERVAL', cast=int)

EMAIL_RETRY_LIMIT = config('EMAIL_RETRY_LIMIT', cast=int)
EMAIL_RETRY_DELAY_SECONDS = config('EMAIL_RETRY_DELAY_SECONDS', cast=int)
NOTIFICATION_QUEUE_SIZE = config('NOTIFICATION_QUEUE_SIZE', cast=int)

AUTH_SESSION_TIMEOUT_MINUTES = config('AUTH_SESSION_TIMEOUT_MINUTES', cast=int)

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
