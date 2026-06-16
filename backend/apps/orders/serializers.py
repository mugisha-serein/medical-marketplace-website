from rest_framework import serializers
from .models import Order, OrderItem, OrderStatusLog


class OrderItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderItem
        fields = [
            'id', 'product', 'product_name_snapshot', 'product_sku_snapshot',
            'unit_price_snapshot', 'quantity', 'subtotal',
        ]
        read_only_fields = fields


class OrderStatusLogSerializer(serializers.ModelSerializer):
    changed_by_email = serializers.EmailField(source='changed_by.email', read_only=True, default=None)

    class Meta:
        model = OrderStatusLog
        fields = ['id', 'from_status', 'to_status', 'changed_by_email', 'notes', 'created_at']
        read_only_fields = fields


class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)
    status_logs = OrderStatusLogSerializer(many=True, read_only=True)

    class Meta:
        model = Order
        fields = [
            'id', 'order_number', 'status', 'shipping_address', 'billing_address',
            'contact_phone', 'notes', 'subtotal', 'shipping_cost', 'tax_amount',
            'total_amount', 'tracking_number', 'estimated_delivery',
            'confirmation_email_sent', 'items', 'status_logs', 'created_at', 'updated_at',
        ]
        read_only_fields = [
            'id', 'order_number', 'status', 'subtotal', 'shipping_cost',
            'tax_amount', 'total_amount', 'tracking_number',
            'confirmation_email_sent', 'created_at', 'updated_at',
        ]


class OrderListSerializer(serializers.ModelSerializer):
    item_count = serializers.SerializerMethodField()

    class Meta:
        model = Order
        fields = [
            'id', 'order_number', 'status', 'total_amount',
            'item_count', 'tracking_number', 'created_at',
        ]
        read_only_fields = fields

    def get_item_count(self, obj):
        return obj.items.count()


class PlaceOrderSerializer(serializers.Serializer):
    shipping_address = serializers.CharField(max_length=1000)
    billing_address = serializers.CharField(max_length=1000)
    contact_phone = serializers.CharField(max_length=30, required=False, allow_blank=True)
    notes = serializers.CharField(max_length=2000, required=False, allow_blank=True)


class TransitionOrderSerializer(serializers.Serializer):
    status = serializers.ChoiceField(choices=Order.Status.choices)
    notes = serializers.CharField(max_length=1000, required=False, allow_blank=True)
    tracking_number = serializers.CharField(max_length=255, required=False, allow_blank=True)