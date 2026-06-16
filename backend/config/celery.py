import os
from celery import Celery
from celery.schedules import crontab

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.development')

app = Celery('medequip')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()

# ── Periodic Tasks (Celery Beat) ──────────────────────────────────────────────
app.conf.beat_schedule = {
    # KPI snapshots every 15 minutes
    'kpi-snapshot-15min': {
        'task': 'apps.kpi.tasks.compute_kpi_snapshot',
        'schedule': crontab(minute='*/15'),
        'kwargs': {'period_type': '15min'},
    },
    # Daily KPI rollup at 00:05 UTC
    'kpi-snapshot-daily': {
        'task': 'apps.kpi.tasks.compute_kpi_snapshot',
        'schedule': crontab(hour=0, minute=5),
        'kwargs': {'period_type': 'daily'},
    },
    # Stock reconciliation daily at 02:00 UTC
    'inventory-reconcile': {
        'task': 'apps.inventory.tasks.reconcile_stock',
        'schedule': crontab(hour=2, minute=0),
    },
    # Cleanup expired carts daily at 03:00 UTC
    'cleanup-expired-carts': {
        'task': 'apps.cart.tasks.cleanup_expired_carts',
        'schedule': crontab(hour=3, minute=0),
    },
    # Retry stuck orders every 5 minutes
    'retry-pending-orders': {
        'task': 'apps.orders.tasks.retry_pending_order_notifications',
        'schedule': crontab(minute='*/5'),
    },
}


@app.task(bind=True, ignore_result=True)
def debug_task(self):
    print(f'Request: {self.request!r}')