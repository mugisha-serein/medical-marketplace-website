import uuid
from django.db import models
from django.core.validators import MinValueValidator


class StockRecord(models.Model):
    """Single source of truth for a product's current stock level."""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    product = models.OneToOneField(
        'catalog.Product', on_delete=models.CASCADE, related_name='stock_record'
    )
    quantity = models.IntegerField(
        default=0,
        validators=[MinValueValidator(0)],
        help_text='Current available stock. Never goes below 0 (DB constraint enforced).',
    )
    reserved_quantity = models.IntegerField(
        default=0,
        validators=[MinValueValidator(0)],
        help_text='Quantity reserved in pending orders.',
    )
    low_stock_threshold = models.IntegerField(default=5)
    allow_backorder = models.BooleanField(default=False)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'inventory_stock_record'
        constraints = [
            models.CheckConstraint(check=models.Q(quantity__gte=0), name='stock_quantity_non_negative'),
            models.CheckConstraint(check=models.Q(reserved_quantity__gte=0), name='stock_reserved_non_negative'),
        ]

    def __str__(self):
        return f'{self.product.name} — qty: {self.quantity}'

    @property
    def available_quantity(self):
        return max(0, self.quantity - self.reserved_quantity)

    @property
    def is_low_stock(self):
        return 0 < self.quantity <= self.low_stock_threshold


class StockMovement(models.Model):
    """Immutable audit log of every stock change."""
    class MovementType(models.TextChoices):
        PURCHASE = 'purchase', 'Purchase / Restock'
        SALE = 'sale', 'Sale'
        RETURN = 'return', 'Return'
        ADJUSTMENT = 'adjustment', 'Manual Adjustment'
        RESERVATION = 'reservation', 'Reservation'
        RESERVATION_RELEASE = 'reservation_release', 'Reservation Release'
        RECONCILE = 'reconcile', 'Reconciliation'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    stock_record = models.ForeignKey(StockRecord, on_delete=models.CASCADE, related_name='movements')
    movement_type = models.CharField(max_length=30, choices=MovementType.choices, db_index=True)
    quantity_delta = models.IntegerField(help_text='Positive = stock in, Negative = stock out')
    quantity_before = models.IntegerField()
    quantity_after = models.IntegerField()
    reference = models.CharField(max_length=255, blank=True, help_text='Order ID, PO number, etc.')
    notes = models.TextField(blank=True)
    created_by = models.ForeignKey(
        'accounts.User', null=True, blank=True, on_delete=models.SET_NULL
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'inventory_stock_movement'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['stock_record', '-created_at'], name='movement_record_date'),
        ]

    def __str__(self):
        return f'{self.movement_type} {self.quantity_delta:+d} on {self.stock_record.product.name}'