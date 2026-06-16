import uuid
from django.db import models


class EmailLog(models.Model):
    """
    Tracks every email dispatch attempt.
    Used for idempotency: check this table before sending to prevent duplicates.
    """
    class EmailType(models.TextChoices):
        WELCOME = 'welcome', 'Welcome'
        ORDER_CONFIRMATION = 'order_confirmation', 'Order Confirmation'
        ORDER_SHIPPED = 'order_shipped', 'Order Shipped'
        ORDER_DELIVERED = 'order_delivered', 'Order Delivered'
        ORDER_CANCELLED = 'order_cancelled', 'Order Cancelled'
        PASSWORD_RESET = 'password_reset', 'Password Reset'
        INQUIRY_RECEIVED = 'inquiry_received', 'Inquiry Received'
        INQUIRY_REPLY = 'inquiry_reply', 'Inquiry Reply'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    recipient_email = models.EmailField(db_index=True)
    email_type = models.CharField(max_length=30, choices=EmailType.choices, db_index=True)
    reference_id = models.CharField(
        max_length=255, db_index=True,
        help_text='Order ID, User ID, or other entity ID this email relates to'
    )
    status = models.CharField(
        max_length=20,
        choices=[('sent', 'Sent'), ('failed', 'Failed'), ('queued', 'Queued')],
        default='queued',
    )
    error_message = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    sent_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 'notifications_email_log'
        # Unique constraint: one email per (type, reference_id) — prevents duplicates
        unique_together = [('email_type', 'reference_id')]
        indexes = [
            models.Index(fields=['recipient_email', 'email_type'], name='emaillog_recipient_type'),
        ]

    def __str__(self):
        return f'{self.email_type} → {self.recipient_email} ({self.status})'