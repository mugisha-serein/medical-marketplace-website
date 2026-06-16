import pytest
from decimal import Decimal
from django.core.cache import cache
from rest_framework.test import APIClient
from rest_framework import status
from django.urls import reverse
from .factories import UserFactory, VendorUserFactory, ProductFactory, OrderFactory, OrderItemFactory
from apps.cart.services import CartService
from apps.orders.models import Order
from apps.inventory.models import StockRecord


@pytest.fixture(autouse=True)
def clear_cache():
    cache.clear()
    yield
    cache.clear()


@pytest.fixture
def customer(db):
    return UserFactory(is_vendor=False)


@pytest.fixture
def auth_client(customer):
    client = APIClient()
    client.force_authenticate(user=customer)
    return client, customer


def setup_cart_with_product(user, quantity=2, stock=10):
    """Helper: creates a product, adds it to the user's cart."""
    product = ProductFactory(
        price=Decimal('1000.00'),
        stock_record=stock,
    )
    CartService.add_item(str(user.id), str(product.id), quantity)
    return product


@pytest.mark.django_db(transaction=True)
class TestOrderPlacement:

    def test_place_order_success(self, db, customer):
        product = setup_cart_with_product(customer, quantity=2, stock=10)

        from apps.orders.services import OrderService
        order = OrderService.place_order(
            user=customer,
            shipping_address='123 Hospital Rd',
            billing_address='123 Hospital Rd',
        )

        assert order.pk is not None
        assert order.status == Order.Status.PENDING
        assert order.items.count() == 1
        assert order.total_amount == Decimal('2000.00')

    def test_order_deducts_stock(self, db, customer):
        product = setup_cart_with_product(customer, quantity=3, stock=10)
        from apps.orders.services import OrderService
        OrderService.place_order(
            user=customer,
            shipping_address='123 Hospital Rd',
            billing_address='123 Hospital Rd',
        )
        product.stock_record.refresh_from_db()
        assert product.stock_record.quantity == 7  # 10 - 3

    def test_order_clears_cart(self, db, customer):
        setup_cart_with_product(customer, quantity=1, stock=5)
        from apps.orders.services import OrderService
        OrderService.place_order(
            user=customer,
            shipping_address='123 Hospital Rd',
            billing_address='123 Hospital Rd',
        )
        cart = CartService.get_cart(str(customer.id))
        assert cart['items'] == {}

    def test_order_items_snapshot_price(self, db, customer):
        product = setup_cart_with_product(customer, quantity=1, stock=5)
        original_price = product.price
        # Change product price AFTER adding to cart
        product.price = Decimal('99999.00')
        product.save()
        from apps.orders.services import OrderService
        order = OrderService.place_order(
            user=customer,
            shipping_address='123 Hospital Rd',
            billing_address='123 Hospital Rd',
        )
        # Order item should use the cart's price snapshot, not the updated price
        item = order.items.first()
        assert item.unit_price_snapshot == original_price

    def test_order_fails_on_insufficient_stock(self, db, customer):
        from apps.orders.services import OrderService, OrderPlacementError
        from apps.cart.services import CartService
        product = ProductFactory(price=Decimal('500.00'), stock_record=1)
        CartService.add_item(str(customer.id), str(product.id), 1)
        # Drain stock after adding to cart
        StockRecord.objects.filter(product=product).update(quantity=0)
        cache.clear()
        with pytest.raises(OrderPlacementError):
            OrderService.place_order(
                user=customer,
                shipping_address='123 Hospital Rd',
                billing_address='123 Hospital Rd',
            )

    def test_order_atomic_rollback_on_second_item_fail(self, db, customer):
        """If second item's stock deduction fails, entire order must roll back."""
        from apps.orders.services import OrderService, OrderPlacementError
        product1 = ProductFactory(price=Decimal('100.00'), stock_record=10)
        product2 = ProductFactory(price=Decimal('200.00'), stock_record=0)
        CartService.add_item(str(customer.id), str(product1.id), 1)
        # Bypass stock check for product2 by directly writing to Redis
        from django.core.cache import cache
        import json
        cart = CartService._load(str(customer.id))
        cart['items'][str(product2.id)] = {
            'qty': 1, 'price_snapshot': '200.00',
            'name': product2.name, 'sku': product2.sku,
            'product_id': str(product2.id),
        }
        CartService._save(str(customer.id), cart)

        initial_stock = product1.stock_record.quantity
        with pytest.raises((OrderPlacementError, Exception)):
            OrderService.place_order(
                user=customer,
                shipping_address='123 Hospital Rd',
                billing_address='123 Hospital Rd',
            )
        # Product1 stock must NOT have changed (rollback)
        product1.stock_record.refresh_from_db()
        assert product1.stock_record.quantity == initial_stock

    def test_order_status_log_created(self, db, customer):
        setup_cart_with_product(customer, quantity=1, stock=5)
        from apps.orders.services import OrderService
        order = OrderService.place_order(
            user=customer,
            shipping_address='123 Hospital Rd',
            billing_address='123 Hospital Rd',
        )
        assert order.status_logs.filter(to_status=Order.Status.PENDING).exists()

    def test_empty_cart_order_fails(self, db, customer):
        from apps.orders.services import OrderService, OrderPlacementError
        with pytest.raises(OrderPlacementError, match='empty'):
            OrderService.place_order(
                user=customer,
                shipping_address='123 Hospital Rd',
                billing_address='123 Hospital Rd',
            )


@pytest.mark.django_db(transaction=True)
class TestOrderStateMachine:

    def test_valid_transition_pending_to_confirmed(self, db):
        order = OrderFactory(status=Order.Status.PENDING)
        from apps.orders.services import OrderService
        order = OrderService.transition_status(order, Order.Status.CONFIRMED)
        assert order.status == Order.Status.CONFIRMED

    def test_invalid_transition_pending_to_delivered_fails(self, db):
        from apps.orders.services import OrderService, OrderTransitionError
        order = OrderFactory(status=Order.Status.PENDING)
        with pytest.raises(OrderTransitionError):
            OrderService.transition_status(order, Order.Status.DELIVERED)

    def test_transition_cancelled_to_any_fails(self, db):
        from apps.orders.services import OrderService, OrderTransitionError
        order = OrderFactory(status=Order.Status.CANCELLED)
        with pytest.raises(OrderTransitionError):
            OrderService.transition_status(order, Order.Status.CONFIRMED)

    def test_status_log_written_on_transition(self, db):
        from apps.orders.services import OrderService
        order = OrderFactory(status=Order.Status.PENDING)
        OrderService.transition_status(order, Order.Status.CONFIRMED, notes='Verified payment')
        log = order.status_logs.latest('created_at')
        assert log.from_status == Order.Status.PENDING
        assert log.to_status == Order.Status.CONFIRMED
        assert log.notes == 'Verified payment'

    def test_cancel_order_restores_stock(self, db):
        product = ProductFactory(price=Decimal('500.00'), stock_record=10)
        order = OrderFactory(status=Order.Status.PENDING)
        OrderItemFactory(
            order=order, product=product, quantity=3,
            unit_price_snapshot=Decimal('500.00'),
        )
        # Deduct stock to simulate what placement would do
        from apps.inventory.services import InventoryService
        InventoryService.deduct(str(product.id), 3, reference=str(order.id))

        from apps.orders.services import OrderService
        OrderService.cancel_order(order, reason='Test cancellation')
        product.stock_record.refresh_from_db()
        assert product.stock_record.quantity == 10  # restored


@pytest.mark.django_db
class TestOrderAPI:

    def test_customer_can_list_own_orders(self, auth_client):
        client, user = auth_client
        OrderFactory(user=user)
        OrderFactory(user=user)
        OrderFactory()  # another user's order
        resp = client.get(reverse('order-list-create'))
        assert resp.status_code == status.HTTP_200_OK
        assert resp.data['count'] == 2

    def test_customer_can_view_own_order(self, auth_client):
        client, user = auth_client
        order = OrderFactory(user=user)
        resp = client.get(reverse('order-detail', kwargs={'order_id': order.id}))
        assert resp.status_code == status.HTTP_200_OK
        assert resp.data['id'] == str(order.id)

    def test_customer_cannot_view_other_order(self, auth_client):
        client, _ = auth_client
        other_order = OrderFactory()
        resp = client.get(reverse('order-detail', kwargs={'order_id': other_order.id}))
        assert resp.status_code == status.HTTP_403_FORBIDDEN

    def test_place_order_via_api(self, db):
        customer = UserFactory(is_vendor=False)
        product = ProductFactory(price=Decimal('500.00'), stock_record=5)
        CartService.add_item(str(customer.id), str(product.id), 1)
        client = APIClient()
        client.force_authenticate(user=customer)
        resp = client.post(reverse('order-list-create'), {
            'shipping_address': '456 Clinic Ave, City',
            'billing_address': '456 Clinic Ave, City',
        })
        assert resp.status_code == status.HTTP_201_CREATED
        assert resp.data['status'] == Order.Status.PENDING
        assert resp.data['total_amount'] == '500.00'

    def test_customer_can_cancel_pending_order(self, auth_client):
        client, user = auth_client
        order = OrderFactory(user=user, status=Order.Status.PENDING)
        resp = client.delete(reverse('order-detail', kwargs={'order_id': order.id}))
        assert resp.status_code == status.HTTP_200_OK
        order.refresh_from_db()
        assert order.status == Order.Status.CANCELLED

    def test_customer_cannot_cancel_shipped_order(self, auth_client):
        client, user = auth_client
        order = OrderFactory(user=user, status=Order.Status.SHIPPED)
        resp = client.delete(reverse('order-detail', kwargs={'order_id': order.id}))
        assert resp.status_code == status.HTTP_400_BAD_REQUEST
