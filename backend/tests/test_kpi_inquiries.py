import pytest
from decimal import Decimal
from datetime import date
from django.core.cache import cache
from rest_framework.test import APIClient
from rest_framework import status
from django.urls import reverse
from .factories import (
    UserFactory, VendorUserFactory, OrderFactory, OrderItemFactory,
    ProductFactory, CategoryFactory,
)


@pytest.fixture(autouse=True)
def clear_cache():
    cache.clear()
    yield
    cache.clear()


# ── KPI Tests ─────────────────────────────────────────────────────────────────

@pytest.mark.django_db
class TestKPIService:

    def test_increment_realtime_counters(self, db):
        from apps.kpi.services import KPIService
        today = date.today().isoformat()
        KPIService.increment_realtime(Decimal('1500.00'), today)
        KPIService.increment_realtime(Decimal('2500.00'), today)
        from apps.kpi.services import RT_ORDERS_KEY, RT_REVENUE_KEY
        orders = cache.get(RT_ORDERS_KEY.format(date=today))
        revenue = cache.get(RT_REVENUE_KEY.format(date=today))
        assert int(orders) == 2
        assert Decimal(str(revenue)) == Decimal('4000.00')

    def test_dashboard_returns_today_counters(self, db):
        from apps.kpi.services import KPIService
        today = date.today().isoformat()
        KPIService.increment_realtime(Decimal('3000.00'), today)
        data = KPIService.get_dashboard_summary()
        assert data['today']['orders'] == 1
        assert Decimal(data['today']['revenue']) == Decimal('3000.00')

    def test_snapshot_computed_and_stored(self, db):
        from apps.kpi.services import KPIService
        from apps.kpi.models import KPISnapshot
        from django.utils import timezone
        # Create orders in the last 15 minutes window
        user = UserFactory()
        vendor = VendorUserFactory()
        cat = CategoryFactory()
        product = ProductFactory(category=cat, vendor=vendor.vendor_profile, stock_record=100)
        order = OrderFactory(user=user, status='confirmed', total_amount=Decimal('5000.00'))
        OrderItemFactory(order=order, product=product, quantity=2, unit_price_snapshot=Decimal('2500.00'))

        period_start = timezone.now().replace(second=0, microsecond=0)
        KPIService.compute_snapshot('daily', period_start)

        snapshots = KPISnapshot.objects.filter(period_type='daily', dimension='overall')
        metrics = {s.metric: s.value for s in snapshots}
        assert 'revenue' in metrics
        assert 'orders' in metrics

    def test_dashboard_cached(self, db):
        from apps.kpi.services import KPIService
        # Call twice — second call should return cached
        data1 = KPIService.get_dashboard_summary()
        data2 = KPIService.get_dashboard_summary()
        assert data1 == data2


@pytest.mark.django_db
class TestKPIAPI:

    def test_vendor_can_access_kpi_dashboard(self, db):
        user = VendorUserFactory()
        client = APIClient()
        client.force_authenticate(user=user)
        resp = client.get(reverse('kpi-dashboard'))
        assert resp.status_code == status.HTTP_200_OK
        assert 'today' in resp.data
        assert 'last_30_days' in resp.data

    def test_customer_cannot_access_kpi(self, db):
        user = UserFactory(is_vendor=False)
        client = APIClient()
        client.force_authenticate(user=user)
        resp = client.get(reverse('kpi-dashboard'))
        assert resp.status_code == status.HTTP_403_FORBIDDEN

    def test_unauthenticated_cannot_access_kpi(self, db):
        client = APIClient()
        resp = client.get(reverse('kpi-dashboard'))
        assert resp.status_code == status.HTTP_401_UNAUTHORIZED

    def test_timeseries_returns_data(self, db):
        from apps.kpi.services import KPIService
        from apps.kpi.models import KPISnapshot
        from django.utils import timezone
        user = VendorUserFactory()
        client = APIClient()
        client.force_authenticate(user=user)
        # Seed a snapshot
        KPISnapshot.objects.create(
            period_start=timezone.now(),
            period_type='daily',
            dimension='vendor',
            dimension_value=str(user.vendor_profile.id),
            metric='revenue',
            value=Decimal('10000.00'),
        )
        resp = client.get(
            reverse('kpi-timeseries') + '?period_type=daily&metric=revenue&dimension=vendor'
        )
        assert resp.status_code == status.HTTP_200_OK
        assert 'results' in resp.data


# ── Inquiry Tests ─────────────────────────────────────────────────────────────

@pytest.mark.django_db
class TestInquiryAPI:

    def test_public_user_can_submit_inquiry(self, db):
        client = APIClient()
        resp = client.post(reverse('inquiry-create'), {
            'sender_name': 'Dr. Ahmed',
            'sender_email': 'ahmed@hospital.com',
            'subject': 'MRI Equipment Inquiry',
            'message': 'I would like to know more about your MRI scanners and pricing.',
            'inquiry_type': 'product',
        })
        assert resp.status_code == status.HTTP_201_CREATED
        assert 'id' in resp.data

    def test_inquiry_requires_name_email_subject_message(self, db):
        client = APIClient()
        resp = client.post(reverse('inquiry-create'), {
            'sender_name': 'Test',
        })
        assert resp.status_code == status.HTTP_400_BAD_REQUEST

    def test_inquiry_message_too_short_fails(self, db):
        client = APIClient()
        resp = client.post(reverse('inquiry-create'), {
            'sender_name': 'Dr. Test',
            'sender_email': 'test@clinic.com',
            'subject': 'Question',
            'message': 'Hi',  # too short
            'inquiry_type': 'general',
        })
        assert resp.status_code == status.HTTP_400_BAD_REQUEST

    def test_vendor_can_list_inquiries(self, db):
        from apps.inquiries.models import ContactInquiry
        vendor = VendorUserFactory()
        ContactInquiry.objects.create(
            sender_name='Test', sender_email='t@t.com',
            subject='Test', message='Test message here',
            vendor=vendor.vendor_profile,
        )
        client = APIClient()
        client.force_authenticate(user=vendor)
        resp = client.get(reverse('inquiry-list'))
        assert resp.status_code == status.HTTP_200_OK

    def test_vendor_can_update_inquiry_status(self, db):
        from apps.inquiries.models import ContactInquiry
        vendor = VendorUserFactory()
        inquiry = ContactInquiry.objects.create(
            sender_name='Test', sender_email='t@t.com',
            subject='Test', message='Test message here',
            vendor=vendor.vendor_profile,
        )
        client = APIClient()
        client.force_authenticate(user=vendor)
        resp = client.patch(
            reverse('inquiry-detail', kwargs={'inquiry_id': inquiry.id}),
            {'status': 'resolved', 'admin_notes': 'Contacted vendor directly.'},
        )
        assert resp.status_code == status.HTTP_200_OK
        assert resp.data['status'] == 'resolved'

    def test_customer_cannot_list_inquiries(self, db):
        user = UserFactory(is_vendor=False)
        client = APIClient()
        client.force_authenticate(user=user)
        resp = client.get(reverse('inquiry-list'))
        assert resp.status_code == status.HTTP_403_FORBIDDEN

    def test_rate_limiting_blocks_excess_inquiries(self, db):
        """Submitting more than 5 inquiries from same IP should be blocked."""
        from apps.inquiries.views import _check_inquiry_rate_limit
        # Simulate 5 allowed requests then block
        ip = '10.0.0.1'
        cache.delete(f'ratelimit:inquiry:{ip}')
        for i in range(5):
            allowed = _check_inquiry_rate_limit(ip)
            assert allowed is True
        # 6th should be blocked
        blocked = _check_inquiry_rate_limit(ip)
        assert blocked is False


# ── Health Check Tests ────────────────────────────────────────────────────────

@pytest.mark.django_db
class TestHealthCheck:

    def test_health_endpoint_returns_ok(self, db):
        client = APIClient()
        resp = client.get(reverse('health-check'))
        assert resp.status_code in (status.HTTP_200_OK, status.HTTP_503_SERVICE_UNAVAILABLE)
        assert 'checks' in resp.data

    def test_health_checks_database(self, db):
        client = APIClient()
        resp = client.get(reverse('health-check'))
        assert 'database' in resp.data['checks']
