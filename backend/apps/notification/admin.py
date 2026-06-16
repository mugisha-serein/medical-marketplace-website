from django.contrib import admin
from .models import EmailLog


@admin.register(EmailLog)
class EmailLogAdmin(admin.ModelAdmin):
    list_display = ['email_type', 'recipient_email', 'reference_id', 'status', 'created_at', 'sent_at']
    list_filter = ['email_type', 'status']
    search_fields = ['recipient_email', 'reference_id']
    readonly_fields = ['id', 'created_at', 'sent_at', 'error_message']
    ordering = ['-created_at']