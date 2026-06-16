import django
import pytest
from django.conf import settings


def pytest_configure(config):
    """Force test settings before Django setup."""
    settings.CELERY_TASK_ALWAYS_EAGER = True
    settings.CELERY_TASK_EAGER_PROPAGATES = True
    # Use in-memory cache for tests
    settings.CACHES = {
        'default': {
            'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        }
    }
    # Use fast password hasher in tests
    settings.PASSWORD_HASHERS = [
        'django.contrib.auth.hashers.MD5PasswordHasher',
    ]
    # Disable axes in tests
    settings.AXES_ENABLED = False
    # Sync email in tests
    settings.EMAIL_BACKEND = 'django.core.mail.backends.locmem.EmailBackend'


@pytest.fixture(scope='session')
def django_db_setup():
    """Session-scoped DB setup — uses --reuse-db from pytest.ini."""
    pass


@pytest.fixture
def admin_user(db):
    from django.contrib.auth import get_user_model
    User = get_user_model()
    return User.objects.create_superuser(
        email='admin@medequip.com',
        password='adminpass123',
    )


@pytest.fixture
def admin_client(admin_user):
    from rest_framework.test import APIClient
    client = APIClient()
    client.force_authenticate(user=admin_user)
    return client, admin_user
