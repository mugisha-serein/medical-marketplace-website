import uuid
from django.db import models


class Inquiry(models.Model):
    class Status(models.TextChoices):
        NEW = 'new', 'New'
        CONTACTED = 'contacted', 'Contacted'
        CLOSED = 'closed', 'Closed'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    product = models.ForeignKey('catalog.Product', null=True, blank=True, on_delete=models.SET_NULL, related_name='inquiries')
    product_name = models.CharField(max_length=255, blank=True)
    buyer_name = models.CharField(max_length=150)
    buyer_email = models.EmailField()
    buyer_phone = models.CharField(max_length=40, blank=True)
    organization = models.CharField(max_length=255, blank=True)
    quantity = models.PositiveIntegerField(default=1)
    message = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.NEW, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'inquiries_inquiry'
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.buyer_name} — {self.product_name or self.product_id}'
