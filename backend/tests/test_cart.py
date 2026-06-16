import pytest
from django.core.cache import cache
from rest_framework.test import APIClient
from rest_framework import status
from django.urls import reverse
from .factories import UserFactory, ProductFactory


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


@pytest.mark.django_db
class TestCartService:

    def test_add_item_to_cart(self, db):
        from apps.cart.services import CartService
        user = UserFactory(is_vendor=False)
        product = ProductFactory(stock_record=10)
        cart = CartService.add_item(str(user.id), str(product.id), 2)
        assert str(product.id) in cart['items']
        assert cart['items'][str(product.id)]['qty'] == 2

    def test_add_item_increments_existing(self, db):
        from apps.cart.services import CartService
        user = UserFactory(is_vendor=False)
        product = ProductFactory(stock_record=10)
        CartService.add_item(str(user.id), str(product.id), 2)
        cart = CartService.add_item(str(user.id), str(product.id), 3)
        assert cart['items'][str(product.id)]['qty'] == 5

    def test_add_item_exceeding_stock_raises(self, db):
        from apps.cart.services import CartService, CartValidationError
        user = UserFactory(is_vendor=False)
        product = ProductFactory(stock_record=3)
        with pytest.raises(CartValidationError):
            CartService.add_item(str(user.id), str(product.id), 10)

    def test_add_inactive_product_raises(self, db):
        from apps.cart.services import CartService, CartValidationError
        user = UserFactory(is_vendor=False)
        product = ProductFactory(is_active=False, stock_record=10)
        with pytest.raises(CartValidationError):
            CartService.add_item(str(user.id), str(product.id), 1)

    def test_update_item_quantity(self, db):
        from apps.cart.services import CartService
        user = UserFactory(is_vendor=False)
        product = ProductFactory(stock_record=10)
        CartService.add_item(str(user.id), str(product.id), 2)
        cart = CartService.update_item(str(user.id), str(product.id), 5)
        assert cart['items'][str(product.id)]['qty'] == 5

    def test_update_item_to_zero_removes_it(self, db):
        from apps.cart.services import CartService
        user = UserFactory(is_vendor=False)
        product = ProductFactory(stock_record=10)
        CartService.add_item(str(user.id), str(product.id), 2)
        cart = CartService.update_item(str(user.id), str(product.id), 0)
        assert str(product.id) not in cart['items']

    def test_remove_item(self, db):
        from apps.cart.services import CartService
        user = UserFactory(is_vendor=False)
        product = ProductFactory(stock_record=10)
        CartService.add_item(str(user.id), str(product.id), 2)
        cart = CartService.remove_item(str(user.id), str(product.id))
        assert str(product.id) not in cart['items']

    def test_clear_cart(self, db):
        from apps.cart.services import CartService
        user = UserFactory(is_vendor=False)
        product = ProductFactory(stock_record=10)
        CartService.add_item(str(user.id), str(product.id), 2)
        CartService.clear(str(user.id))
        cart = CartService.get_cart(str(user.id))
        assert cart['items'] == {}

    def test_cart_total_calculation(self, db):
        from apps.cart.services import CartService
        from decimal import Decimal
        user = UserFactory(is_vendor=False)
        product1 = ProductFactory(price=Decimal('100.00'), stock_record=10)
        product2 = ProductFactory(price=Decimal('250.00'), stock_record=10)
        CartService.add_item(str(user.id), str(product1.id), 2)
        cart = CartService.add_item(str(user.id), str(product2.id), 1)
        assert Decimal(cart['total']) == Decimal('450.00')

    def test_validate_for_checkout_empty_cart_raises(self, db):
        from apps.cart.services import CartService, CartValidationError
        user = UserFactory(is_vendor=False)
        with pytest.raises(CartValidationError, match='empty'):
            CartService.validate_for_checkout(str(user.id))

    def test_validate_for_checkout_insufficient_stock_raises(self, db):
        from apps.cart.services import CartService, CartValidationError
        user = UserFactory(is_vendor=False)
        product = ProductFactory(stock_record=1)
        # Add 2 items but only 1 in stock — then reduce stock to 0
        CartService.add_item(str(user.id), str(product.id), 1)
        # Simulate stock being bought by someone else
        from apps.inventory.models import StockRecord
        StockRecord.objects.filter(product=product).update(quantity=0)
        cache.clear()  # ensure fresh stock check
        with pytest.raises(CartValidationError):
            CartService.validate_for_checkout(str(user.id))


@pytest.mark.django_db
class TestCartAPI:

    def test_get_empty_cart(self, auth_client):
        client, _ = auth_client
        resp = client.get(reverse('cart'))
        assert resp.status_code == status.HTTP_200_OK
        assert resp.data['items'] == {}

    def test_add_item_via_api(self, auth_client):
        client, _ = auth_client
        product = ProductFactory(stock_record=10)
        resp = client.post(reverse('cart-item-add'), {
            'product_id': str(product.id),
            'quantity': 2,
        })
        assert resp.status_code == status.HTTP_200_OK
        assert str(product.id) in resp.data['items']

    def test_add_item_invalid_quantity(self, auth_client):
        client, _ = auth_client
        product = ProductFactory(stock_record=10)
        resp = client.post(reverse('cart-item-add'), {
            'product_id': str(product.id),
            'quantity': 0,
        })
        assert resp.status_code == status.HTTP_400_BAD_REQUEST

    def test_update_item_via_api(self, auth_client):
        client, user = auth_client
        product = ProductFactory(stock_record=10)
        from apps.cart.services import CartService
        CartService.add_item(str(user.id), str(product.id), 1)
        resp = client.patch(
            reverse('cart-item-detail', kwargs={'product_id': product.id}),
            {'quantity': 3},
        )
        assert resp.status_code == status.HTTP_200_OK
        assert resp.data['items'][str(product.id)]['qty'] == 3

    def test_delete_item_via_api(self, auth_client):
        client, user = auth_client
        product = ProductFactory(stock_record=10)
        from apps.cart.services import CartService
        CartService.add_item(str(user.id), str(product.id), 2)
        resp = client.delete(
            reverse('cart-item-detail', kwargs={'product_id': product.id})
        )
        assert resp.status_code == status.HTTP_200_OK
        assert str(product.id) not in resp.data['items']

    def test_clear_cart_via_api(self, auth_client):
        client, user = auth_client
        product = ProductFactory(stock_record=10)
        from apps.cart.services import CartService
        CartService.add_item(str(user.id), str(product.id), 2)
        resp = client.delete(reverse('cart'))
        assert resp.status_code == status.HTTP_200_OK

    def test_unauthenticated_cart_access_denied(self):
        client = APIClient()
        resp = client.get(reverse('cart'))
        assert resp.status_code == status.HTTP_401_UNAUTHORIZED
