import logging
import time
import random
from django.db import transaction, OperationalError
from apps.inventory.models import StockRecord, StockMovement

logger = logging.getLogger(__name__)

MAX_LOCK_RETRIES = 3
LOCK_RETRY_BASE_MS = 100


class InsufficientStockError(Exception):
    def __init__(self, product_id, requested, available):
        self.product_id = product_id
        self.requested = requested
        self.available = available
        super().__init__(
            f'Insufficient stock for product {product_id}: '
            f'requested {requested}, available {available}'
        )


class StockLockError(Exception):
    pass


class InventoryService:
    """
    All stock mutations flow through this service.
    Uses SELECT FOR UPDATE (NOWAIT) to prevent overselling.
    Every mutation writes a StockMovement for full audit trail.
    """

    @staticmethod
    def _acquire_lock(product_id: str) -> StockRecord:
        """
        Attempts SELECT FOR UPDATE NOWAIT.
        Retries up to MAX_LOCK_RETRIES times with jittered backoff.
        Raises StockLockError if lock cannot be acquired.
        """
        for attempt in range(MAX_LOCK_RETRIES):
            try:
                return StockRecord.objects.select_for_update(nowait=True).get(
                    product_id=product_id
                )
            except OperationalError:
                if attempt == MAX_LOCK_RETRIES - 1:
                    raise StockLockError(f'Could not acquire stock lock for product {product_id}')
                jitter = random.randint(0, 50)
                wait_ms = LOCK_RETRY_BASE_MS * (2 ** attempt) + jitter
                time.sleep(wait_ms / 1000)
            except StockRecord.DoesNotExist:
                raise InsufficientStockError(product_id, 0, 0)

    @staticmethod
    @transaction.atomic
    def deduct(product_id: str, quantity: int, reference: str = '', user=None) -> StockRecord:
        """
        Atomically deducts stock. Called inside order placement transaction.
        Raises InsufficientStockError if stock is insufficient.
        """
        stock = InventoryService._acquire_lock(product_id)

        if stock.quantity < quantity:
            raise InsufficientStockError(product_id, quantity, stock.quantity)

        qty_before = stock.quantity
        stock.quantity -= quantity
        stock.save(update_fields=['quantity', 'updated_at'])

        StockMovement.objects.create(
            stock_record=stock,
            movement_type=StockMovement.MovementType.SALE,
            quantity_delta=-quantity,
            quantity_before=qty_before,
            quantity_after=stock.quantity,
            reference=reference,
            created_by=user,
        )
        logger.info('Stock deducted', extra={
            'product_id': str(product_id), 'qty': quantity,
            'after': stock.quantity, 'ref': reference,
        })
        return stock

    @staticmethod
    @transaction.atomic
    def restock(product_id: str, quantity: int, reference: str = '', notes: str = '', user=None) -> StockRecord:
        """Adds stock (purchase/restock)."""
        stock = InventoryService._acquire_lock(product_id)
        qty_before = stock.quantity
        stock.quantity += quantity
        stock.save(update_fields=['quantity', 'updated_at'])

        StockMovement.objects.create(
            stock_record=stock,
            movement_type=StockMovement.MovementType.PURCHASE,
            quantity_delta=quantity,
            quantity_before=qty_before,
            quantity_after=stock.quantity,
            reference=reference,
            notes=notes,
            created_by=user,
        )
        return stock

    @staticmethod
    @transaction.atomic
    def adjust(product_id: str, quantity_delta: int, reason: str = '', user=None) -> StockRecord:
        """Manual adjustment (positive or negative)."""
        stock = InventoryService._acquire_lock(product_id)
        new_qty = stock.quantity + quantity_delta
        if new_qty < 0:
            raise InsufficientStockError(product_id, abs(quantity_delta), stock.quantity)

        qty_before = stock.quantity
        stock.quantity = new_qty
        stock.save(update_fields=['quantity', 'updated_at'])

        StockMovement.objects.create(
            stock_record=stock,
            movement_type=StockMovement.MovementType.ADJUSTMENT,
            quantity_delta=quantity_delta,
            quantity_before=qty_before,
            quantity_after=stock.quantity,
            notes=reason,
            created_by=user,
        )
        return stock

    @staticmethod
    def check_availability(product_id: str, quantity: int) -> bool:
        """Non-locking optimistic check. Used for pre-validation only."""
        try:
            stock = StockRecord.objects.get(product_id=product_id)
            return stock.quantity >= quantity or stock.allow_backorder
        except StockRecord.DoesNotExist:
            return False

    @staticmethod
    def get_stock(product_id: str) -> StockRecord | None:
        try:
            return StockRecord.objects.get(product_id=product_id)
        except StockRecord.DoesNotExist:
            return None

    @staticmethod
    @transaction.atomic
    def reconcile(product_id: str, user=None):
        """
        Re-derives quantity from StockMovement history.
        Corrects drift and writes a reconcile movement if needed.
        Called daily by Celery beat.
        """
        stock = InventoryService._acquire_lock(product_id)
        from django.db.models import Sum
        derived = StockMovement.objects.filter(
            stock_record=stock
        ).aggregate(total=Sum('quantity_delta'))['total'] or 0

        if derived != stock.quantity:
            logger.critical(
                'Stock reconciliation mismatch',
                extra={'product_id': str(product_id), 'stored': stock.quantity, 'derived': derived}
            )
            qty_before = stock.quantity
            stock.quantity = max(0, derived)
            stock.save(update_fields=['quantity', 'updated_at'])
            StockMovement.objects.create(
                stock_record=stock,
                movement_type=StockMovement.MovementType.RECONCILE,
                quantity_delta=stock.quantity - qty_before,
                quantity_before=qty_before,
                quantity_after=stock.quantity,
                notes='Automatic daily reconciliation',
                created_by=user,
            )
        return stock
