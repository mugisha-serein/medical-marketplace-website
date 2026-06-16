"""Notification service with async Celery delivery."""
from typing import Dict, Any, Optional
from django.core.mail import send_mail
from django.template.loader import render_to_string
from infrastructure.services import BaseService
from infrastructure.logging import get_logger

logger = get_logger(__name__)


class NotificationService(BaseService):
    """
    Async notification delivery via Celery.
    
    Rules:
    - All notifications async via Celery
    - Idempotent delivery (same message ID = idempotent)
    - Retry-safe tasks
    - Delivery logging for audit trail
    """
    
    @staticmethod
    def send_email(
        recipient_email: str,
        subject: str,
        html_message: str,
        plain_text_message: str = None,
        from_email: str = 'noreply@medequip.com',
        async_delivery: bool = True
    ) -> Dict[str, Any]:
        """
        Send email notification.
        
        Args:
            recipient_email: Recipient email
            subject: Email subject
            html_message: HTML content
            plain_text_message: Plain text fallback
            from_email: Sender email
            async_delivery: Queue for async delivery
        
        Returns:
            Notification metadata
        """
        notification_id = None
        
        if async_delivery:
            # Queue via Celery
            from apps.notification.tasks import send_email_task
            
            result = send_email_task.apply_async(
                kwargs={
                    'recipient_email': recipient_email,
                    'subject': subject,
                    'html_message': html_message,
                    'plain_text_message': plain_text_message,
                    'from_email': from_email,
                },
                retry=True,
                max_retries=5
            )
            notification_id = result.id
            
            logger.info(
                f'Email queued for delivery',
                extra={
                    'recipient': recipient_email,
                    'subject': subject,
                    'task_id': notification_id,
                }
            )
        else:
            # Send synchronously (for testing)
            try:
                send_mail(
                    subject=subject,
                    message=plain_text_message or html_message,
                    from_email=from_email,
                    recipient_list=[recipient_email],
                    html_message=html_message,
                    fail_silently=False,
                )
                logger.info(
                    f'Email sent',
                    extra={'recipient': recipient_email, 'subject': subject}
                )
            except Exception as e:
                logger.error(
                    f'Email send failed',
                    extra={'recipient': recipient_email, 'error': str(e)},
                    exc_info=True
                )
                raise
        
        return {
            'notification_id': notification_id,
            'recipient': recipient_email,
            'type': 'email',
            'status': 'queued' if async_delivery else 'sent',
        }
    
    @staticmethod
    def send_order_confirmation(order: Any) -> Dict[str, Any]:
        """Send order confirmation email."""
        context = {
            'order_number': order.order_number,
            'total_amount': order.total_amount,
            'user_name': order.user.full_name,
        }
        
        html_message = render_to_string('emails/order_confirmation.html', context)
        plain_text = f'Order {order.order_number} confirmed. Total: {order.total_amount}'
        
        return NotificationService.send_email(
            recipient_email=order.user.email,
            subject=f'Order Confirmation - {order.order_number}',
            html_message=html_message,
            plain_text_message=plain_text,
        )
    
    @staticmethod
    def send_shipment_notification(order: Any, tracking_number: str) -> Dict[str, Any]:
        """Send shipment notification."""
        context = {
            'order_number': order.order_number,
            'tracking_number': tracking_number,
            'user_name': order.user.full_name,
        }
        
        html_message = render_to_string('emails/shipment_notification.html', context)
        plain_text = f'Your order {order.order_number} has shipped. Tracking: {tracking_number}'
        
        return NotificationService.send_email(
            recipient_email=order.user.email,
            subject=f'Your Order Has Shipped - {order.order_number}',
            html_message=html_message,
            plain_text_message=plain_text,
        )
    
    @staticmethod
    def send_delivery_confirmation(order: Any) -> Dict[str, Any]:
        """Send delivery confirmation."""
        context = {
            'order_number': order.order_number,
            'user_name': order.user.full_name,
        }
        
        html_message = render_to_string('emails/delivery_confirmation.html', context)
        plain_text = f'Your order {order.order_number} has been delivered'
        
        return NotificationService.send_email(
            recipient_email=order.user.email,
            subject=f'Delivery Confirmed - {order.order_number}',
            html_message=html_message,
            plain_text_message=plain_text,
        )


__all__ = ['NotificationService']
