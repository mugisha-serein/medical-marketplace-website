from rest_framework import serializers, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.contrib import admin
from django.db import transaction

from config.permission import IsVendorOrAdmin
from .models import StockRecord, StockMovement
from .services import InventoryService, InsufficientStockError


# ── Serializers ───────────────────────────────────────────────────────────────
class StockRecordSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source='product.name', read_only=True)
    product_sku = serializers.CharField(source='product.sku', read_only=True)
    is_low_stock = serializers.BooleanField(read_only=True)
    available_quantity = serializers.IntegerField(read_only=True)

    class Meta:
        model = StockRecord
        fields = [
            'id', 'product', 'product_name', 'product_sku',
            'quantity', 'reserved_quantity', 'available_quantity',
            'low_stock_threshold', 'allow_backorder', 'is_low_stock', 'updated_at',
        ]
        read_only_fields = ['id', 'quantity', 'reserved_quantity', 'updated_at']


class StockMovementSerializer(serializers.ModelSerializer):
    class Meta:
        model = StockMovement
        fields = [
            'id', 'movement_type', 'quantity_delta', 'quantity_before',
            'quantity_after', 'reference', 'notes', 'created_at',
        ]
        read_only_fields = fields


class AdjustStockSerializer(serializers.Serializer):
    quantity_delta = serializers.IntegerField()
    reason = serializers.CharField(max_length=500, required=False, allow_blank=True)


class RestockSerializer(serializers.Serializer):
    quantity = serializers.IntegerField(min_value=1)
    reference = serializers.CharField(max_length=255, required=False, allow_blank=True)
    notes = serializers.CharField(max_length=500, required=False, allow_blank=True)


# ── Views ─────────────────────────────────────────────────────────────────────
class StockDetailView(APIView):
    permission_classes = [IsVendorOrAdmin]

    def _get_stock(self, product_id, user):
        from apps.catalog.models import Product
        try:
            product = Product.objects.get(pk=product_id)
        except Product.DoesNotExist:
            return None, Response({'error': 'Product not found.'}, status=status.HTTP_404_NOT_FOUND)
        if not user.is_staff and getattr(user, 'vendor_profile', None) != product.vendor:
            return None, Response({'error': 'Permission denied.'}, status=status.HTTP_403_FORBIDDEN)
        stock = InventoryService.get_stock(product_id)
        if not stock:
            return None, Response({'error': 'Stock record not found.'}, status=status.HTTP_404_NOT_FOUND)
        return stock, None

    def get(self, request, product_id):
        stock, err = self._get_stock(product_id, request.user)
        if err:
            return err
        return Response(StockRecordSerializer(stock).data)

    def patch(self, request, product_id):
        """Adjust stock by delta."""
        stock, err = self._get_stock(product_id, request.user)
        if err:
            return err
        serializer = AdjustStockSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            stock = InventoryService.adjust(
                product_id=str(product_id),
                quantity_delta=serializer.validated_data['quantity_delta'],
                reason=serializer.validated_data.get('reason', ''),
                user=request.user,
            )
        except InsufficientStockError as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        return Response(StockRecordSerializer(stock).data)


class RestockView(APIView):
    permission_classes = [IsVendorOrAdmin]

    def post(self, request, product_id):
        from apps.catalog.models import Product
        try:
            product = Product.objects.get(pk=product_id)
        except Product.DoesNotExist:
            return Response({'error': 'Product not found.'}, status=status.HTTP_404_NOT_FOUND)
        if not request.user.is_staff and getattr(request.user, 'vendor_profile', None) != product.vendor:
            return Response({'error': 'Permission denied.'}, status=status.HTTP_403_FORBIDDEN)
        serializer = RestockSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        stock = InventoryService.restock(
            product_id=str(product_id),
            quantity=serializer.validated_data['quantity'],
            reference=serializer.validated_data.get('reference', ''),
            notes=serializer.validated_data.get('notes', ''),
            user=request.user,
        )
        return Response(StockRecordSerializer(stock).data)


class StockMovementListView(APIView):
    permission_classes = [IsVendorOrAdmin]

    def get(self, request, product_id):
        from apps.catalog.models import Product
        try:
            product = Product.objects.get(pk=product_id)
        except Product.DoesNotExist:
            return Response({'error': 'Product not found.'}, status=status.HTTP_404_NOT_FOUND)
        if not request.user.is_staff and getattr(request.user, 'vendor_profile', None) != product.vendor:
            return Response({'error': 'Permission denied.'}, status=status.HTTP_403_FORBIDDEN)
        movements = StockMovement.objects.filter(
            stock_record__product_id=product_id
        ).order_by('-created_at')[:100]
        return Response(StockMovementSerializer(movements, many=True).data)


# ── Admin ─────────────────────────────────────────────────────────────────────
@admin.register(StockRecord)
class StockRecordAdmin(admin.ModelAdmin):
    list_display = ['product', 'quantity', 'reserved_quantity', 'low_stock_threshold', 'allow_backorder', 'updated_at']
    list_filter = ['allow_backorder']
    search_fields = ['product__name', 'product__sku']
    readonly_fields = ['quantity', 'reserved_quantity', 'updated_at']


@admin.register(StockMovement)
class StockMovementAdmin(admin.ModelAdmin):
    list_display = ['stock_record', 'movement_type', 'quantity_delta', 'quantity_after', 'reference', 'created_at']
    list_filter = ['movement_type']
    search_fields = ['reference', 'stock_record__product__name']
    readonly_fields = list(StockMovementSerializer.Meta.fields)