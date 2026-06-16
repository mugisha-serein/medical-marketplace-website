import logging
from decimal import Decimal
from celery import shared_task
from django.utils import timezone

logger = logging.getLogger(__name__)


@shared_task(
    bind=True,
    autoretry_for=(Exception,),
    retry_backoff=True,
    retry_backoff_max=300,
    max_retries=3,
    name='apps.kpi.tasks.compute_kpi_snapshot',
)
def compute_kpi_snapshot(self, period_type: str = 'daily'):
    from .services import KPIService
    now = timezone.now()

    if period_type == '15min':
        # Align to last complete 15-min window
        minutes = (now.minute // 15) * 15
        period_start = now.replace(minute=minutes, second=0, microsecond=0)
        # Use the previous window to ensure it's complete
        from datetime import timedelta
        period_start -= timedelta(minutes=15)
    elif period_type == 'daily':
        period_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
    else:
        period_start = now.replace(minute=0, second=0, microsecond=0)

    KPIService.compute_snapshot(period_type, period_start)
    return {'period_type': period_type, 'period_start': str(period_start)}


@shared_task(
    bind=True,
    autoretry_for=(Exception,),
    retry_backoff=True,
    max_retries=5,
    name='apps.kpi.tasks.increment_realtime_kpi',
)
def increment_realtime_kpi(self, order_total: str, order_date: str):
    """Atomic Redis counter increment. Called post-commit on every order placement."""
    from .services import KPIService
    KPIService.increment_realtime(
        order_total=Decimal(order_total),
        order_date=order_date,
    )
    logger.info('Real-time KPI incremented', extra={'date': order_date, 'total': order_total})