import uuid
from django.db import models
from django.utils import timezone


class Cart(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(
        'accounts.User', on_delete=models.CASCADE, related_name='cart'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    expires_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 'cart_cart'

    def __str__(self):
        return f'Cart({self.user.email})'

    @property
    def total(self):
        return sum(item.line_total for item in self.items.all())

    @property
    def item_count(self):
        return sum(item.quantity for item in self.items.all())


class CartItem(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(
        'catalog.Product', on_delete=models.CASCADE, related_name='cart_items'
    )
    quantity = models.PositiveIntegerField(default=1)
    # Price snapshot at time of add — locked at checkout
    price_at_add = models.DecimalField(max_digits=12, decimal_places=2)
    added_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'cart_item'
        unique_together = [('cart', 'product')]
        constraints = [
            models.CheckConstraint(check=models.Q(quantity__gte=1), name='cartitem_qty_min_1'),
        ]

    def __str__(self):
        return f'{self.quantity}x {self.product.name}'

    @property
    def line_total(self):
        return self.price_at_add * self.quantity

    @property
    def current_price(self):
        return self.product.price

    @property
    def price_changed(self):
        return self.price_at_add != self.product.price