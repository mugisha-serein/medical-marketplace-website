import logging
from celery import shared_task
from .models import StockRecord
from .services import InventoryService

logger = logging.getLogger(__name__)


@shared_task(
    bind=True,
    autoretry_for=(Exception,),
    retry_backoff=True,
    retry_backoff_max=600,
    max_retries=3,
    name='apps.inventory.tasks.reconcile_stock',
)
def reconcile_stock(self):
    """Daily task: re-derives all stock quantities from movement history."""
    product_ids = StockRecord.objects.values_list('product_id', flat=True)
    mismatches = 0
    for product_id in product_ids:
        try:
            InventoryService.reconcile(str(product_id))
        except Exception as exc:
            logger.error('Reconcile failed for product %s: %s', product_id, exc)
            mismatches += 1
    logger.info('Stock reconciliation complete. Mismatches corrected: %d', mismatches)
    return {'mismatches': mismatches}


@shared_task(
    bind=True,
    name='apps.inventory.tasks.create_stock_record',
)
def create_stock_record(self, product_id: str, initial_quantity: int = 0):
    """Creates a StockRecord for a newly created product."""
    from apps.catalog.models import Product
    try:
        product = Product.objects.get(pk=product_id)
        StockRecord.objects.get_or_create(
            product=product,
            defaults={'quantity': initial_quantity},
        )
        logger.info('StockRecord created for product %s', product_id)
    except Exception as exc:
        logger.error('Failed to create StockRecord for %s: %s', product_id, exc)
        raise self.retry(exc=exc)