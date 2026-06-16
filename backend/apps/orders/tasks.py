import logging
from celery import shared_task
from django.utils import timezone
from datetime import timedelta

logger = logging.getLogger(__name__)


@shared_task(
    bind=True,
    autoretry_for=(Exception,),
    retry_backoff=True,
    retry_backoff_max=600,
    max_retries=5,
    name='apps.orders.tasks.retry_pending_order_notifications',
)
def retry_pending_order_notifications(self):
    """
    Scans for orders placed >10 min ago with no confirmation email sent.
    Dispatches the email task idempotently.
    Runs every 5 minutes via Celery beat.
    """
    from .models import Order
    from apps.notification.tasks import send_order_confirmation_email

    cutoff = timezone.now() - timedelta(minutes=10)
    stuck_orders = Order.objects.filter(
        confirmation_email_sent=False,
        created_at__lte=cutoff,
        status__in=[Order.Status.PENDING, Order.Status.CONFIRMED],
    ).values_list('id', flat=True)

    count = 0
    for order_id in stuck_orders:
        send_order_confirmation_email.delay(str(order_id))
        count += 1

    if count:
        logger.warning('Re-dispatched %d stuck order confirmation emails.', count)

    return {'dispatched': count}
