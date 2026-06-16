from rest_framework import serializers


class PaymentInitiationSerializer(serializers.Serializer):
    order_id = serializers.UUIDField()
    provider = serializers.CharField()


class PaymentResponseSerializer(serializers.Serializer):
    id = serializers.UUIDField(read_only=True)
    order = serializers.UUIDField(read_only=True)
    status = serializers.CharField(read_only=True)
    provider = serializers.CharField(read_only=True)
    amount = serializers.DecimalField(max_digits=14, decimal_places=2, read_only=True)
    currency = serializers.CharField(read_only=True)
    created_at = serializers.DateTimeField(read_only=True)

