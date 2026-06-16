import uuid
from django.db import models
from django.utils import timezone


class Order(models.Model):
    class Status(models.TextChoices):
        PENDING = 'pending', 'Pending'
        CONFIRMED = 'confirmed', 'Confirmed'
        PROCESSING = 'processing', 'Processing'
        SHIPPED = 'shipped', 'Shipped'
        DELIVERED = 'delivered', 'Delivered'
        CANCELLED = 'cancelled', 'Cancelled'
        REFUNDED = 'refunded', 'Refunded'

    # Valid state machine transitions
    VALID_TRANSITIONS = {
        Status.PENDING: [Status.CONFIRMED, Status.CANCELLED],
        Status.CONFIRMED: [Status.PROCESSING, Status.CANCELLED],
        Status.PROCESSING: [Status.SHIPPED, Status.CANCELLED],
        Status.SHIPPED: [Status.DELIVERED],
        Status.DELIVERED: [Status.REFUNDED],
        Status.CANCELLED: [],
        Status.REFUNDED: [],
    }

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    order_number = models.CharField(max_length=32, unique=True, db_index=True)
    user = models.ForeignKey(
        'accounts.User', on_delete=models.PROTECT, related_name='orders'
    )
    status = models.CharField(
        max_length=20, choices=Status.choices, default=Status.PENDING, db_index=True
    )

    # Snapshot of delivery address at order time
    shipping_address = models.TextField()
    billing_address = models.TextField()
    contact_phone = models.CharField(max_length=30, blank=True)
    notes = models.TextField(blank=True)

    # Financials — all snapshots, never recalculated from live data
    subtotal = models.DecimalField(max_digits=14, decimal_places=2)
    shipping_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    tax_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total_amount = models.DecimalField(max_digits=14, decimal_places=2)

    # Tracking
    tracking_number = models.CharField(max_length=255, blank=True)
    estimated_delivery = models.DateField(null=True, blank=True)

    # Notification state — for the retry task
    confirmation_email_sent = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'orders_order'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', '-created_at'], name='order_user_date'),
            models.Index(fields=['status', '-created_at'], name='order_status_date'),
        ]

    def __str__(self):
        return f'Order {self.order_number} ({self.status})'

    def can_transition_to(self, new_status: str) -> bool:
        return new_status in self.VALID_TRANSITIONS.get(self.status, [])

    @staticmethod
    def generate_order_number() -> str:
        import random, string
        prefix = 'ME'
        timestamp = timezone.now().strftime('%Y%m%d')
        suffix = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
        return f'{prefix}{timestamp}{suffix}'


class OrderItem(models.Model):
    """Immutable snapshot of what was ordered. Never joins back to live Product for financials."""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')

    # FK for reference only — all financial fields are snapshots
    product = models.ForeignKey(
        'catalog.Product', on_delete=models.SET_NULL, null=True, related_name='order_items'
    )
    vendor = models.ForeignKey(
        'accounts.VendorProfile', on_delete=models.SET_NULL, null=True, related_name='order_items'
    )

    # Snapshots — immutable after creation
    product_name_snapshot = models.CharField(max_length=500)
    product_sku_snapshot = models.CharField(max_length=100)
    unit_price_snapshot = models.DecimalField(max_digits=12, decimal_places=2)
    quantity = models.PositiveIntegerField()
    subtotal = models.DecimalField(max_digits=14, decimal_places=2)

    class Meta:
        db_table = 'orders_order_item'
        indexes = [
            models.Index(fields=['product'], name='orderitem_product'),
        ]

    def save(self, *args, **kwargs):
        self.subtotal = self.unit_price_snapshot * self.quantity
        super().save(*args, **kwargs)

    def __str__(self):
        return f'{self.quantity}x {self.product_name_snapshot}'


class OrderStatusLog(models.Model):
    """Audit trail of every status transition."""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='status_logs')
    from_status = models.CharField(max_length=20, blank=True)
    to_status = models.CharField(max_length=20)
    changed_by = models.ForeignKey(
        'accounts.User', null=True, blank=True, on_delete=models.SET_NULL
    )
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'orders_status_log'
        ordering = ['-created_at']

    def __str__(self):
        return f'Order {self.order.order_number}: {self.from_status} → {self.to_status}'