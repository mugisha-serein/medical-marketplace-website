from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from config.permission import IsVendorOrAdmin
from .models import Order
from .serializers import (
    OrderSerializer, OrderListSerializer,
    PlaceOrderSerializer, TransitionOrderSerializer,
)
from .services import OrderService, OrderPlacementError, OrderTransitionError


class OrderListCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        """Customer: see own orders. Staff: see all."""
        if request.user.is_staff:
            qs = Order.objects.prefetch_related('items').order_by('-created_at')
        else:
            qs = Order.objects.filter(user=request.user).prefetch_related('items').order_by('-created_at')

        # Simple filter by status
        status_filter = request.query_params.get('status')
        if status_filter:
            qs = qs.filter(status=status_filter)

        # Manual pagination
        page_size = min(int(request.query_params.get('page_size', 20)), 100)
        page = max(int(request.query_params.get('page', 1)), 1)
        start = (page - 1) * page_size
        total = qs.count()
        results = qs[start:start + page_size]

        return Response({
            'count': total,
            'page': page,
            'page_size': page_size,
            'results': OrderListSerializer(results, many=True).data,
        })

    def post(self, request):
        """Place a new order from the customer's cart."""
        serializer = PlaceOrderSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            order = OrderService.place_order(
                user=request.user,
                **serializer.validated_data,
            )
        except OrderPlacementError as e:
            return Response(
                {'error': str(e), 'details': e.errors},
                status=status.HTTP_400_BAD_REQUEST,
            )
        return Response(
            OrderSerializer(order).data,
            status=status.HTTP_201_CREATED,
        )


class OrderDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def _get_order(self, order_id, user):
        try:
            order = Order.objects.prefetch_related(
                'items', 'status_logs'
            ).get(pk=order_id)
        except Order.DoesNotExist:
            return None, Response({'error': 'Order not found.'}, status=status.HTTP_404_NOT_FOUND)
        if not user.is_staff and order.user != user:
            return None, Response({'error': 'Permission denied.'}, status=status.HTTP_403_FORBIDDEN)
        return order, None

    def get(self, request, order_id):
        order, err = self._get_order(order_id, request.user)
        if err:
            return err
        return Response(OrderSerializer(order).data)

    def delete(self, request, order_id):
        """Customer can cancel pending orders."""
        order, err = self._get_order(order_id, request.user)
        if err:
            return err
        if order.status not in (Order.Status.PENDING, Order.Status.CONFIRMED):
            return Response(
                {'error': f'Cannot cancel order in status {order.status}.'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        try:
            order = OrderService.cancel_order(
                order, cancelled_by=request.user, reason='Cancelled by customer.'
            )
        except OrderTransitionError as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        return Response(OrderSerializer(order).data)


class OrderStatusTransitionView(APIView):
    """Admin / vendor-facing status transitions."""
    permission_classes = [IsVendorOrAdmin]

    def post(self, request, order_id):
        try:
            order = Order.objects.get(pk=order_id)
        except Order.DoesNotExist:
            return Response({'error': 'Order not found.'}, status=status.HTTP_404_NOT_FOUND)

        # Vendor can only see orders containing their products
        if not request.user.is_staff and request.user.is_vendor:
            vendor = getattr(request.user, 'vendor_profile', None)
            if not order.items.filter(vendor=vendor).exists():
                return Response({'error': 'Permission denied.'}, status=status.HTTP_403_FORBIDDEN)

        serializer = TransitionOrderSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            order = OrderService.transition_status(
                order=order,
                new_status=serializer.validated_data['status'],
                changed_by=request.user,
                notes=serializer.validated_data.get('notes', ''),
                tracking_number=serializer.validated_data.get('tracking_number', ''),
            )
        except OrderTransitionError as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

        return Response(OrderSerializer(order).data)


class VendorOrderListView(APIView):
    """Vendor sees orders that contain their products."""
    permission_classes = [IsVendorOrAdmin]

    def get(self, request):
        if request.user.is_staff:
            qs = Order.objects.all()
        else:
            vendor = getattr(request.user, 'vendor_profile', None)
            qs = Order.objects.filter(items__vendor=vendor).distinct()

        status_filter = request.query_params.get('status')
        if status_filter:
            qs = qs.filter(status=status_filter)

        qs = qs.prefetch_related('items').order_by('-created_at')
        page_size = min(int(request.query_params.get('page_size', 20)), 100)
        page = max(int(request.query_params.get('page', 1)), 1)
        start = (page - 1) * page_size
        total = qs.count()

        return Response({
            'count': total,
            'page': page,
            'page_size': page_size,
            'results': OrderListSerializer(qs[start:start + page_size], many=True).data,
        })