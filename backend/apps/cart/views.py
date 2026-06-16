from rest_framework import serializers, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .services import CartService, CartValidationError


# ── Serializers ───────────────────────────────────────────────────────────────
class AddCartItemSerializer(serializers.Serializer):
    product_id = serializers.UUIDField()
    quantity = serializers.IntegerField(min_value=1, max_value=999)


class UpdateCartItemSerializer(serializers.Serializer):
    quantity = serializers.IntegerField(min_value=0, max_value=999)


# ── Views ─────────────────────────────────────────────────────────────────────
class CartView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        cart = CartService.get_cart(str(request.user.id))
        return Response(cart)

    def delete(self, request):
        CartService.clear(str(request.user.id))
        return Response({'message': 'Cart cleared.'}, status=status.HTTP_200_OK)


class CartItemView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        """Add item to cart."""
        serializer = AddCartItemSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            cart = CartService.add_item(
                user_id=str(request.user.id),
                product_id=str(serializer.validated_data['product_id']),
                quantity=serializer.validated_data['quantity'],
            )
        except CartValidationError as e:
            return Response(
                {'error': str(e), 'details': e.errors},
                status=status.HTTP_400_BAD_REQUEST,
            )
        return Response(cart, status=status.HTTP_200_OK)

    def patch(self, request, product_id):
        """Update item quantity."""
        serializer = UpdateCartItemSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            cart = CartService.update_item(
                user_id=str(request.user.id),
                product_id=str(product_id),
                quantity=serializer.validated_data['quantity'],
            )
        except CartValidationError as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        return Response(cart)

    def delete(self, request, product_id):
        """Remove item from cart."""
        cart = CartService.remove_item(
            user_id=str(request.user.id),
            product_id=str(product_id),
        )
        return Response(cart)