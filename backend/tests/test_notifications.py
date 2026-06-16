import pytest
from unittest.mock import patch, MagicMock
from django.core.cache import cache
from .factories import UserFactory, OrderFactory, OrderItemFactory


@pytest.fixture(autouse=True)
def clear_cache():
    cache.clear()
    yield
    cache.clear()


@pytest.mark.django_db
class TestEmailIdempotency:

    def test_welcome_email_sent_once(self, db):
        from apps.notification.tasks import _idempotent_send
        from apps.notification.models import EmailLog
        user = UserFactory()

        with patch('apps.notification.tasks.send_mail') as mock_send:
            mock_send.return_value = 1
            # First send
            result1 = _idempotent_send(
                email_type=EmailLog.EmailType.WELCOME,
                reference_id=str(user.id),
                recipient=user.email,
                subject='Welcome',
                body='Welcome to MedEquip!',
            )
            # Second send (duplicate)
            result2 = _idempotent_send(
                email_type=EmailLog.EmailType.WELCOME,
                reference_id=str(user.id),
                recipient=user.email,
                subject='Welcome',
                body='Welcome to MedEquip!',
            )

        assert result1 is True   # First send allowed
        assert result2 is False  # Duplicate blocked
        assert mock_send.call_count == 1  # Only called once

    def test_order_confirmation_email_marks_order(self, db):
        from apps.notification.tasks import send_order_confirmation_email
        user = UserFactory()
        order = OrderFactory(user=user)
        OrderItemFactory(order=order)

        with patch('apps.notification.tasks.send_mail') as mock_send:
            mock_send.return_value = 1
            send_order_confirmation_email(str(order.id))

        order.refresh_from_db()
        assert order.confirmation_email_sent is True

    def test_order_confirmation_not_resent(self, db):
        from apps.notification.tasks import send_order_confirmation_email
        from apps.notification.models import EmailLog
        user = UserFactory()
        order = OrderFactory(user=user)
        OrderItemFactory(order=order)

        with patch('apps.notification.tasks.send_mail') as mock_send:
            mock_send.return_value = 1
            send_order_confirmation_email(str(order.id))
            send_order_confirmation_email(str(order.id))  # duplicate call

        # send_mail only called once despite two task calls
        assert mock_send.call_count == 1

    def test_email_log_status_updated_on_send(self, db):
        from apps.notification.tasks import _idempotent_send
        from apps.notification.models import EmailLog
        user = UserFactory()

        with patch('apps.notification.tasks.send_mail') as mock_send:
            mock_send.return_value = 1
            _idempotent_send(
                email_type=EmailLog.EmailType.WELCOME,
                reference_id=str(user.id),
                recipient=user.email,
                subject='Welcome',
                body='Body',
            )

        log = EmailLog.objects.get(email_type=EmailLog.EmailType.WELCOME, reference_id=str(user.id))
        assert log.status == 'sent'
        assert log.sent_at is not None

    def test_email_log_status_failed_on_error(self, db):
        from apps.notification.tasks import _idempotent_send
        from apps.notification.models import EmailLog
        user = UserFactory()

        with patch('apps.notification.tasks.send_mail', side_effect=Exception('SMTP down')):
            with pytest.raises(Exception, match='SMTP down'):
                _idempotent_send(
                    email_type=EmailLog.EmailType.WELCOME,
                    reference_id=str(user.id) + '-fail',
                    recipient=user.email,
                    subject='Welcome',
                    body='Body',
                )

        log = EmailLog.objects.filter(
            email_type=EmailLog.EmailType.WELCOME
        ).latest('created_at')
        assert log.status == 'failed'
        assert 'SMTP down' in log.error_message

    def test_order_status_email_shipped(self, db):
        from apps.notification.tasks import send_order_status_email
        user = UserFactory()
        order = OrderFactory(user=user, tracking_number='TRACK-001')

        with patch('apps.notification.tasks.send_mail') as mock_send:
            mock_send.return_value = 1
            send_order_status_email(str(order.id), 'shipped')

        assert mock_send.called
        call_args = mock_send.call_args
        assert 'shipped' in call_args[1]['subject'].lower() or 'shipped' in call_args[0][0].lower()

    def test_nonexistent_order_does_not_crash(self, db):
        """Tasks should silently skip if order doesn't exist."""
        from apps.notification.tasks import send_order_confirmation_email
        # Should not raise
        send_order_confirmation_email('00000000-0000-0000-0000-000000000000')


@pytest.mark.django_db
class TestInquiryEmailDispatch:

    def test_inquiry_email_dispatched(self, db):
        from apps.inquiries.models import ContactInquiry
        from apps.notification.tasks import send_inquiry_email
        from tests.factories import VendorUserFactory

        vendor = VendorUserFactory()
        inquiry = ContactInquiry.objects.create(
            sender_name='Dr. Test',
            sender_email='doctor@hospital.com',
            subject='Equipment Query',
            message='Need pricing for your MRI equipment.',
            vendor=vendor.vendor_profile,
        )

        with patch('apps.notification.tasks.send_mail') as mock_send:
            mock_send.return_value = 1
            send_inquiry_email(str(inquiry.id))

        # Should send to both vendor and sender
        assert mock_send.call_count >= 1
