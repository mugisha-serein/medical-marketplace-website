from django.contrib import admin
from .models import Order, OrderItem, OrderStatusLog


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = [
        'product', 'product_name_snapshot', 'product_sku_snapshot',
        'unit_price_snapshot', 'quantity', 'subtotal',
    ]
    can_delete = False


class OrderStatusLogInline(admin.TabularInline):
    model = OrderStatusLog
    extra = 0
    readonly_fields = ['from_status', 'to_status', 'changed_by', 'notes', 'created_at']
    can_delete = False


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = [
        'order_number', 'user', 'status', 'total_amount',
        'confirmation_email_sent', 'created_at',
    ]
    list_filter = ['status', 'confirmation_email_sent']
    search_fields = ['order_number', 'user__email']
    readonly_fields = [
        'id', 'order_number', 'subtotal', 'tax_amount', 'total_amount', 'created_at', 'updated_at',
    ]
    inlines = [OrderItemInline, OrderStatusLogInline]
    ordering = ['-created_at']