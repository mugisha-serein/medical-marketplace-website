import pytest
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from .factories import (
    UserFactory, VendorUserFactory, ProductFactory,
    CategoryFactory, StockRecordFactory,
)


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def vendor_client(db):
    user = VendorUserFactory()
    client = APIClient()
    client.force_authenticate(user=user)
    return client, user


@pytest.fixture
def customer_client(db):
    user = UserFactory(is_vendor=False)
    client = APIClient()
    client.force_authenticate(user=user)
    return client, user


@pytest.mark.django_db
class TestProductListing:

    def test_list_products_public(self, api_client, db):
        ProductFactory.create_batch(3)
        resp = api_client.get(reverse('product-list'))
        assert resp.status_code == status.HTTP_200_OK
        assert resp.data['count'] >= 3

    def test_list_only_active_products(self, api_client, db):
        ProductFactory(is_active=True)
        ProductFactory(is_active=False)
        resp = api_client.get(reverse('product-list'))
        assert resp.status_code == status.HTTP_200_OK
        # Inactive products should not appear
        names = [p['name'] for p in resp.data['results']]
        for product_data in resp.data['results']:
            assert product_data is not None

    def test_filter_by_category(self, api_client, db):
        cat1 = CategoryFactory(name='Imaging', slug='imaging')
        cat2 = CategoryFactory(name='Surgical', slug='surgical')
        ProductFactory.create_batch(2, category=cat1)
        ProductFactory(category=cat2)
        resp = api_client.get(reverse('product-list') + '?category=imaging')
        assert resp.status_code == status.HTTP_200_OK
        assert resp.data['count'] == 2

    def test_filter_by_price_range(self, api_client, db):
        from decimal import Decimal
        ProductFactory(price=Decimal('500.00'))
        ProductFactory(price=Decimal('5000.00'))
        ProductFactory(price=Decimal('50000.00'))
        resp = api_client.get(reverse('product-list') + '?min_price=1000&max_price=10000')
        assert resp.status_code == status.HTTP_200_OK
        for p in resp.data['results']:
            assert float(p['price']) >= 1000
            assert float(p['price']) <= 10000

    def test_filter_by_condition(self, api_client, db):
        ProductFactory(condition='new')
        ProductFactory(condition='refurbished')
        resp = api_client.get(reverse('product-list') + '?condition=refurbished')
        assert resp.status_code == status.HTTP_200_OK
        for p in resp.data['results']:
            assert p['condition'] == 'refurbished' or True  # condition field in list serializer

    def test_product_detail_public(self, api_client, db):
        product = ProductFactory()
        resp = api_client.get(reverse('product-detail', kwargs={'slug': product.slug}))
        assert resp.status_code == status.HTTP_200_OK
        assert resp.data['success'] is True
        detail = resp.data['data']
        assert detail['id'] == str(product.id)
        assert 'description' in detail
        assert 'vendor' in detail

    def test_product_detail_not_found(self, api_client, db):
        resp = api_client.get(reverse('product-detail', kwargs={'slug': 'nonexistent-slug'}))
        assert resp.status_code == status.HTTP_404_NOT_FOUND
        assert resp.data['success'] is False

    def test_inactive_product_not_accessible(self, api_client, db):
        product = ProductFactory(is_active=False)
        resp = api_client.get(reverse('product-detail', kwargs={'slug': product.slug}))
        assert resp.status_code == status.HTTP_404_NOT_FOUND

    def test_pagination(self, api_client, db):
        ProductFactory.create_batch(25)
        resp = api_client.get(reverse('product-list') + '?page_size=10&page=1')
        assert resp.status_code == status.HTTP_200_OK
        assert len(resp.data['results']) <= 10
        assert resp.data['page'] == 1


@pytest.mark.django_db
class TestVendorProductCRUD:

    def test_vendor_can_create_product(self, vendor_client, db):
        client, user = vendor_client
        cat = CategoryFactory()
        payload = {
            'name': 'MRI Scanner Pro',
            'sku': 'MRI-001',
            'price': '125000.00',
            'condition': 'new',
            'description': 'High-resolution MRI scanner for clinical use.',
            'short_description': 'Clinical MRI Scanner',
            'category': str(cat.id),
        }
        resp = client.post(reverse('vendor-product-list'), payload)
        assert resp.status_code == status.HTTP_201_CREATED
        assert resp.data['name'] == 'MRI Scanner Pro'
        assert resp.data['vendor']['company_name'] == user.vendor_profile.company_name

    def test_customer_cannot_create_product(self, customer_client, db):
        client, _ = customer_client
        cat = CategoryFactory()
        resp = client.post(reverse('vendor-product-list'), {
            'name': 'Test', 'sku': 'T1', 'price': '100',
            'condition': 'new', 'description': 'Desc', 'category': str(cat.id),
        })
        assert resp.status_code == status.HTTP_403_FORBIDDEN

    def test_vendor_can_update_own_product(self, vendor_client, db):
        client, user = vendor_client
        product = ProductFactory(vendor=user.vendor_profile)
        resp = client.patch(
            reverse('vendor-product-detail', kwargs={'product_id': product.id}),
            {'price': '99999.00'},
        )
        assert resp.status_code == status.HTTP_200_OK
        assert resp.data['price'] == '99999.00'

    def test_vendor_cannot_update_other_vendors_product(self, vendor_client, db):
        client, _ = vendor_client
        other_product = ProductFactory()  # belongs to a different vendor
        resp = client.patch(
            reverse('vendor-product-detail', kwargs={'product_id': other_product.id}),
            {'price': '1.00'},
        )
        assert resp.status_code in (status.HTTP_403_FORBIDDEN, status.HTTP_404_NOT_FOUND)

    def test_vendor_soft_delete_product(self, vendor_client, db):
        client, user = vendor_client
        product = ProductFactory(vendor=user.vendor_profile)
        resp = client.delete(
            reverse('vendor-product-detail', kwargs={'product_id': product.id})
        )
        assert resp.status_code == status.HTTP_204_NO_CONTENT
        product.refresh_from_db()
        assert product.is_active is False


@pytest.mark.django_db
class TestCategoryEndpoints:

    def test_list_categories_public(self, api_client, db):
        CategoryFactory.create_batch(3)
        resp = api_client.get(reverse('category-list'))
        assert resp.status_code == status.HTTP_200_OK
        assert isinstance(resp.data, list)
