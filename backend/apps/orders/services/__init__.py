import logging
from decimal import Decimal
from django.db import transaction
from django.utils import timezone

from apps.cart.services import CartService, CartValidationError
from apps.inventory.services import InventoryService, InsufficientStockError, StockLockError
from apps.orders.models import Order, OrderItem, OrderStatusLog

logger = logging.getLogger(__name__)


class OrderPlacementError(Exception):
    def __init__(self, message, errors=None):
        self.errors = errors or []
        super().__init__(message)


class OrderTransitionError(Exception):
    pass


class OrderService:

    @staticmethod
    @transaction.atomic
    def place_order(user, shipping_address: str, billing_address: str,
                    contact_phone: str = '', notes: str = '') -> Order:
        """
        Atomic order placement.

        Flow:
          1. Validate + lock cart
          2. SELECT FOR UPDATE on each StockRecord (via InventoryService.deduct)
          3. Create Order + OrderItems (price snapshots)
          4. Clear cart
          5. COMMIT
          Post-commit: emit Celery tasks (email, KPI increment)

        Any failure rolls back entirely. No partial orders.
        """
        user_id = str(user.id)

        # Step 1: Full cart validation (stock + active product check)
        try:
            validated = CartService.validate_for_checkout(user_id)
        except CartValidationError as e:
            raise OrderPlacementError(str(e), errors=e.errors)

        validated_items = validated['items']

        # Step 2: Compute order totals
        financials = OrderService.calculate_order_totals(validated_items)
        subtotal = financials['subtotal']
        shipping_cost = financials['shipping_cost']
        tax_amount = financials['tax_amount']
        total_amount = financials['total_amount']

        # Step 3: Create Order (inside atomic block)
        order = Order.objects.create(
            order_number=Order.generate_order_number(),
            user=user,
            status=Order.Status.PENDING,
            shipping_address=shipping_address,
            billing_address=billing_address,
            contact_phone=contact_phone,
            notes=notes,
            subtotal=subtotal,
            shipping_cost=shipping_cost,
            tax_amount=tax_amount,
            total_amount=total_amount,
        )

        # Step 4: Deduct stock (SELECT FOR UPDATE per product) + create OrderItems
        order_items = []
        for product_id, item_data in validated_items.items():
            try:
                InventoryService.deduct(
                    product_id=product_id,
                    quantity=item_data['qty'],
                    reference=str(order.id),
                    user=user,
                )
            except (InsufficientStockError, StockLockError) as e:
                # Roll back entire transaction
                raise OrderPlacementError(
                    f'Stock error for product {item_data.get("name", product_id)}: {e}',
                    errors=[{'product_id': product_id, 'error': str(e)}]
                )

            product_obj = item_data.get('product')
            unit_price = Decimal(str(item_data['price_snapshot']))
            order_items.append(OrderItem(
                order=order,
                product=product_obj,
                vendor=product_obj.vendor if product_obj else None,
                product_name_snapshot=item_data['name'],
                product_sku_snapshot=item_data['sku'],
                unit_price_snapshot=unit_price,
                quantity=item_data['qty'],
                subtotal=unit_price * item_data['qty']  # bulk_create won't call save()
            ))

        OrderItem.objects.bulk_create(order_items)

        # Step 5: Log initial status
        OrderStatusLog.objects.create(
            order=order,
            from_status='',
            to_status=Order.Status.PENDING,
            changed_by=user,
            notes='Order placed by customer.',
        )

        # Step 6: Clear cart (still inside atomic block)
        CartService.clear(user_id)

        logger.info('Order placed', extra={
            'order_id': str(order.id),
            'order_number': order.order_number,
            'user_id': user_id,
            'total': str(total_amount),
            'item_count': len(order_items),
        })

        # Step 7: Post-commit async tasks
        transaction.on_commit(lambda: OrderService._post_place_tasks(order))

        return order

    @staticmethod
    def calculate_order_totals(validated_items: dict) -> dict:
        """Pure function for order financial calculations."""
        subtotal = Decimal('0.00')
        for item_data in validated_items.values():
            qty = item_data['qty']
            price = Decimal(str(item_data['price_snapshot']))
            subtotal += price * qty

        shipping_cost = Decimal('0.00')  # Placeholder for future logic
        tax_amount = (subtotal * Decimal('0.00'))  # Placeholder for future logic
        
        return {
            'subtotal': subtotal,
            'shipping_cost': shipping_cost,
            'tax_amount': tax_amount,
            'total_amount': subtotal + shipping_cost + tax_amount
        }

    @staticmethod
    def _post_place_tasks(order: Order):
        """Dispatched after transaction commits. Never blocks the response."""
        from apps.notification.tasks import send_order_confirmation_email
        from apps.kpi.tasks import increment_realtime_kpi
        send_order_confirmation_email.delay(str(order.id))
        increment_realtime_kpi.delay(
            order_total=str(order.total_amount),
            order_date=order.created_at.date().isoformat(),
        )

    @staticmethod
    @transaction.atomic
    def transition_status(order: Order, new_status: str, changed_by=None,
                          notes: str = '', tracking_number: str = '') -> Order:
        """
        Enforces the state machine. Only valid transitions allowed.
        Admin or vendor-facing; not exposed to customers directly.
        """
        if not order.can_transition_to(new_status):
            raise OrderTransitionError(
                f'Cannot transition order from {order.status} to {new_status}.'
            )

        old_status = order.status
        order.status = new_status
        if tracking_number:
            order.tracking_number = tracking_number
        order.save(update_fields=['status', 'tracking_number', 'updated_at'])

        OrderStatusLog.objects.create(
            order=order,
            from_status=old_status,
            to_status=new_status,
            changed_by=changed_by,
            notes=notes,
        )

        logger.info('Order status changed', extra={
            'order_id': str(order.id),
            'from': old_status,
            'to': new_status,
        })

        # Notify customer on key transitions
        transaction.on_commit(lambda: OrderService._notify_status_change(order, new_status))

        return order

    @staticmethod
    def _notify_status_change(order: Order, new_status: str):
        from apps.notification.tasks import send_order_status_email
        if new_status in (Order.Status.SHIPPED, Order.Status.DELIVERED, Order.Status.CANCELLED):
            send_order_status_email.delay(str(order.id), new_status)

    @staticmethod
    def cancel_order(order: Order, cancelled_by=None, reason: str = '') -> Order:
        """Cancel and restore stock if items were deducted."""
        order = OrderService.transition_status(
            order, Order.Status.CANCELLED, changed_by=cancelled_by, notes=reason
        )
        # Restore stock for each item
        for item in order.items.select_related('product').all():
            if item.product_id:
                InventoryService.restock(
                    product_id=str(item.product_id),
                    quantity=item.quantity,
                    reference=str(order.id),
                    notes=f'Order {order.order_number} cancelled.',
                    user=cancelled_by,
                )
        return order
