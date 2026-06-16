"""Celery tasks for async notification delivery."""
import logging
from django.utils import timezone
from django.core.mail import send_mail
from django.conf import settings
from celery import shared_task
from infrastructure.logging import get_logger
from infrastructure.metrics import MetricsCollector
from .models import EmailLog

logger = get_logger(__name__)

FROM_EMAIL = getattr(settings, 'DEFAULT_FROM_EMAIL', 'noreply@medequip.com')


@shared_task(
    bind=True,
    autoretry_for=(Exception,),
    retry_backoff=True,
    retry_backoff_max=600,
    max_retries=5,
    name='apps.notification.tasks.send_email_task',
)
def send_email_task(
    self,
    recipient_email: str,
    subject: str,
    html_message: str,
    plain_text_message: str = None,
    from_email: str = None,
):
    """Generic async email task used by NotificationService."""
    send_mail(
        subject=subject,
        message=plain_text_message or html_message,
        from_email=from_email or FROM_EMAIL,
        recipient_list=[recipient_email],
        html_message=html_message,
        fail_silently=False,
    )
    MetricsCollector.record_async_task('send_email_task', 0, success=True)


def _idempotent_send(
    email_type: str,
    reference_id: str,
    recipient: str,
    subject: str,
    body: str,
    html_message: str = None
) -> bool:
    """
    Send email with idempotency via EmailLog.
    Returns True if sent, False if already sent (idempotency guard).
    """
    log, created = EmailLog.objects.get_or_create(
        email_type=email_type,
        reference_id=reference_id,
        defaults={
            'recipient_email': recipient,
            'status': 'queued',
        },
    )

    if not created and log.status == 'sent':
        logger.info(
            f'Email already sent (idempotency)',
            extra={
                'email_type': email_type,
                'reference_id': reference_id,
                'recipient': recipient,
            }
        )
        return False

    try:
        send_mail(
            subject=subject,
            message=body,
            from_email=FROM_EMAIL,
            recipient_list=[recipient],
            html_message=html_message,
            fail_silently=False,
        )
        log.status = 'sent'
        log.sent_at = timezone.now()
        log.save(update_fields=['status', 'sent_at'])
        
        logger.info(
            f'Email sent',
            extra={
                'email_type': email_type,
                'reference_id': reference_id,
                'recipient': recipient,
            }
        )
        
        return True
    except Exception as exc:
        log.status = 'failed'
        log.error_message = str(exc)
        log.save(update_fields=['status', 'error_message'])
        logger.error(
            f'Email send failed',
            extra={
                'email_type': email_type,
                'reference_id': reference_id,
                'recipient': recipient,
                'error': str(exc),
            },
            exc_info=True
        )
        raise  # allow Celery to retry


@shared_task(
    bind=True,
    autoretry_for=(Exception,),
    retry_backoff=True,
    retry_backoff_max=600,
    max_retries=5,
    name='apps.notification.tasks.send_welcome_email',
)
def send_welcome_email(self, user_id: str):
    """Send welcome email after user registration."""
    from django.contrib.auth import get_user_model
    
    User = get_user_model()
    try:
        user = User.objects.get(pk=user_id)
    except User.DoesNotExist:
        logger.warning(f'User not found for welcome email: {user_id}')
        return

    _idempotent_send(
        email_type=EmailLog.EmailType.WELCOME,
        reference_id=user_id,
        recipient=user.email,
        subject='Welcome to MedEquip!',
        body=(
            f'Hi {user.first_name or user.email},\n\n'
            'Welcome to MedEquip — your trusted marketplace for hospital equipment.\n\n'
            'Browse our catalog at https://medequip.com/catalog\n\n'
            'Best regards,\nThe MedEquip Team'
        ),
    )
    
    MetricsCollector.record_async_task('send_welcome_email', 0, success=True)


@shared_task(
    bind=True,
    autoretry_for=(Exception,),
    retry_backoff=True,
    retry_backoff_max=600,
    max_retries=5,
    name='apps.notification.tasks.send_order_confirmation_email',
)
def send_order_confirmation_email(self, order_id: str):
    """Send order confirmation email."""
    from apps.orders.models import Order

    try:
        order = Order.objects.select_related('user').prefetch_related('items').get(pk=order_id)
    except Order.DoesNotExist:
        logger.warning(f'Order not found for confirmation email: {order_id}')
        return

    items_text = '\n'.join(
        f'  - Product x{item.quantity} @ ${item.unit_price_snapshot}'
        for item in order.items.all()
    ) if hasattr(order, 'items') else 'See order details'

    sent = _idempotent_send(
        email_type=EmailLog.EmailType.ORDER_CONFIRMATION,
        reference_id=order_id,
        recipient=order.user.email,
        subject=f'Order Confirmed — {order.order_number}',
        body=(
            f'Hi {order.user.first_name or order.user.email},\n\n'
            f'Your order {order.order_number} has been received.\n\n'
            f'Items:\n{items_text}\n\n'
            f'Total: ${order.total_amount}\n\n'
            f'Shipping to: {order.shipping_address}\n\n'
            'We will notify you when your order ships.\n\n'
            'MedEquip Team'
        ),
    )

    if sent:
        Order.objects.filter(pk=order_id).update(confirmation_email_sent=True)

    MetricsCollector.record_async_task('send_order_confirmation_email', 0, success=True)


@shared_task(
    bind=True,
    autoretry_for=(Exception,),
    retry_backoff=True,
    retry_backoff_max=600,
    max_retries=5,
    name='apps.notification.tasks.send_order_status_email',
)
def send_order_status_email(self, order_id: str, new_status: str):
    """Send order status change notification."""
    from apps.orders.models import Order

    try:
        order = Order.objects.select_related('user').get(pk=order_id)
    except Order.DoesNotExist:
        logger.warning(f'Order not found for status email: {order_id}')
        return

    status_messages = {
        'shipped': (
            f'Your order {order.order_number} has been shipped!',
            f'Tracking number: {order.tracking_number or "Not yet available"}\n'
            f'Estimated delivery: {order.estimated_delivery or "TBD"}',
        ),
        'delivered': (
            f'Your order {order.order_number} has been delivered!',
            'Thank you for shopping with MedEquip.',
        ),
        'cancelled': (
            f'Your order {order.order_number} has been cancelled.',
            'If you did not request this cancellation, please contact support.',
        ),
    }

    if new_status not in status_messages:
        logger.warning(f'Unknown order status for email: {new_status}')
        return

    subject, body_text = status_messages[new_status]

    email_type_by_status = {
        'shipped': EmailLog.EmailType.ORDER_SHIPPED,
        'delivered': EmailLog.EmailType.ORDER_DELIVERED,
        'cancelled': EmailLog.EmailType.ORDER_CANCELLED,
    }

    _idempotent_send(
        email_type=email_type_by_status[new_status],
        reference_id=f'{order_id}_{new_status}',
        recipient=order.user.email,
        subject=subject,
        body=body_text,
    )
    
    MetricsCollector.record_async_task('send_order_status_email', 0, success=True)


__all__ = [
    'send_email_task',
    'send_welcome_email',
    'send_order_confirmation_email',
    'send_order_status_email',
]

@shared_task(
    bind=True,
    autoretry_for=(Exception,),
    retry_backoff=True,
    retry_backoff_max=300,
    max_retries=3,
    name='apps.notification.tasks.send_inquiry_email',
)
def send_inquiry_email(self, inquiry_id: str):
    try:
        from apps.inquiries.models import ContactInquiry
    except ImportError:
        logger.warning('ContactInquiry model is not available for inquiry email task.')
        return
    try:
        inquiry = ContactInquiry.objects.select_related('vendor').get(pk=inquiry_id)
    except ContactInquiry.DoesNotExist:
        return

    # Email to vendor (if vendor inquiry)
    if inquiry.vendor:
        _idempotent_send(
            email_type=EmailLog.EmailType.INQUIRY_RECEIVED,
            reference_id=f'{inquiry_id}:vendor',
            recipient=inquiry.vendor.user.email,
            subject=f'New Inquiry: {inquiry.subject}',
            body=(
                f'You have a new inquiry from {inquiry.sender_name} ({inquiry.sender_email}).\n\n'
                f'Subject: {inquiry.subject}\n\n'
                f'Message:\n{inquiry.message}\n\n'
                'Please log in to MedEquip to respond.'
            ),
        )

    # Auto-reply to sender
    _idempotent_send(
        email_type=EmailLog.EmailType.INQUIRY_RECEIVED,
        reference_id=f'{inquiry_id}:sender',
        recipient=inquiry.sender_email,
        subject=f'We received your inquiry: {inquiry.subject}',
        body=(
            f'Hi {inquiry.sender_name},\n\n'
            'Thank you for your inquiry. We have received your message and will respond shortly.\n\n'
            'MedEquip Team'
        ),
    )
