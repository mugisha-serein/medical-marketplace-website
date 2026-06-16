import logging
from celery import shared_task
from django.core.cache import cache
from django.contrib.auth import get_user_model

logger = logging.getLogger(__name__)
User = get_user_model()


@shared_task(name='apps.cart.tasks.cleanup_expired_carts')
def cleanup_expired_carts():
    """
    Redis TTL handles expiry automatically.
    This task logs stats and can do any additional cleanup.
    """
    logger.info('Cart cleanup task ran (Redis TTL handles automatic expiry).')
    return {'status': 'ok'}