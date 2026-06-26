from rest_framework import serializers
from apps.catalog.models import Product
from .models import Inquiry


class InquirySerializer(serializers.ModelSerializer):
    product_slug = serializers.SlugRelatedField(
        source='product',
        slug_field='slug',
        queryset=Product.objects.all(),
        required=False,
        allow_null=True,
        write_only=True,
    )

    class Meta:
        model = Inquiry
        fields = [
            'id', 'product', 'product_slug', 'product_name', 'buyer_name',
            'buyer_email', 'buyer_phone', 'organization', 'quantity',
            'message', 'status', 'created_at',
        ]
        read_only_fields = ['id', 'product', 'status', 'created_at']

    def validate_quantity(self, value):
        if value < 1:
            raise serializers.ValidationError('Quantity must be at least 1.')
        return value

    def create(self, validated_data):
        product = validated_data.get('product')
        if product and not validated_data.get('product_name'):
            validated_data['product_name'] = product.name
        return super().create(validated_data)
