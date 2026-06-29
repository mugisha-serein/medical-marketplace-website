from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework.parsers import MultiPartParser, FormParser

from config.permission import IsVendorOrAdmin
from .models import Product, Category, Tag, ProductImage
from .serializers import (
    ProductListSerializer, ProductDetailSerializer, ProductCreateUpdateSerializer,
    CategorySerializer, TagSerializer, ProductImageSerializer,
)
from .services import SearchService, ProductService


def success_response(data=None, message='OK', status_code=status.HTTP_200_OK):
    return Response({'success': True, 'message': message, 'data': data}, status=status_code)


def error_response(message, error_code='ERROR', status_code=status.HTTP_400_BAD_REQUEST):
    return Response({'success': False, 'message': message, 'error_code': error_code}, status=status_code)


class ProductListView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        params = {
            'q': request.query_params.get('q', ''),
            'category_slug': request.query_params.get('category'),
            'min_price': request.query_params.get('min_price'),
            'max_price': request.query_params.get('max_price'),
            'condition': request.query_params.get('condition'),
            'vendor_id': request.query_params.get('vendor_id'),
            'is_featured': request.query_params.get('is_featured') == 'true',
            'ordering': request.query_params.get('ordering', '-created_at'),
        }
        for key in ('min_price', 'max_price'):
            if params[key]:
                try:
                    params[key] = float(params[key])
                except ValueError:
                    params[key] = None

        queryset = SearchService.search(params)
        page_size = min(int(request.query_params.get('page_size', 20)), 100)
        page = max(int(request.query_params.get('page', 1)), 1)
        start = (page - 1) * page_size
        end = start + page_size
        results = list(queryset) if not isinstance(queryset, list) else queryset
        serializer = ProductListSerializer(results[start:end], many=True, context={'request': request})
        return Response({
            'count': len(results),
            'page': page,
            'page_size': page_size,
            'results': serializer.data,
        })


class ProductDetailView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, slug):
        try:
            product = Product.objects.select_related('vendor', 'category').prefetch_related(
                'images', 'tags'
            ).get(slug=slug, is_active=True)
        except Product.DoesNotExist:
            return error_response('Product not found.', 'NOT_FOUND', status.HTTP_404_NOT_FOUND)
        serializer = ProductDetailSerializer(product, context={'request': request})
        return success_response(serializer.data, 'Product retrieved successfully.')


class VendorProductListCreateView(APIView):
    permission_classes = [IsVendorOrAdmin]

    def get(self, request):
        if request.user.is_staff:
            qs = Product.objects.all()
        else:
            qs = Product.objects.filter(vendor=request.user.vendor_profile)
        qs = qs.select_related('vendor', 'category').prefetch_related('images', 'tags').order_by('-created_at')
        serializer = ProductListSerializer(qs, many=True, context={'request': request})
        return Response(serializer.data)

    def post(self, request):
        serializer = ProductCreateUpdateSerializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        product = serializer.save()
        return Response(
            ProductDetailSerializer(product, context={'request': request}).data,
            status=status.HTTP_201_CREATED,
        )


class VendorProductDetailView(APIView):
    permission_classes = [IsVendorOrAdmin]

    def get_object(self, product_id, user):
        try:
            product = Product.objects.select_related('vendor', 'category').prefetch_related(
                'images', 'tags'
            ).get(pk=product_id)
        except Product.DoesNotExist:
            return None, error_response('Product not found.', 'NOT_FOUND', status.HTTP_404_NOT_FOUND)
        if not user.is_staff and product.vendor != getattr(user, 'vendor_profile', None):
            return None, error_response('Permission denied.', 'FORBIDDEN', status.HTTP_403_FORBIDDEN)
        return product, None

    def get(self, request, product_id):
        product, err = self.get_object(product_id, request.user)
        if err:
            return err
        return success_response(
            ProductDetailSerializer(product, context={'request': request}).data,
            'Product retrieved successfully.'
        )

    def patch(self, request, product_id):
        product, err = self.get_object(product_id, request.user)
        if err:
            return err
        serializer = ProductCreateUpdateSerializer(
            product, data=request.data, partial=True, context={'request': request}
        )
        serializer.is_valid(raise_exception=True)
        product = serializer.save()
        return success_response(
            ProductDetailSerializer(product, context={'request': request}).data,
            'Product updated successfully.'
        )

    def delete(self, request, product_id):
        product, err = self.get_object(product_id, request.user)
        if err:
            return err
        product.is_active = False
        product.save(update_fields=['is_active'])
        ProductService.invalidate_product_cache(str(product.pk))
        return Response(status=status.HTTP_204_NO_CONTENT)


class ProductImageUploadView(APIView):
    permission_classes = [IsVendorOrAdmin]
    parser_classes = [MultiPartParser, FormParser]

    def post(self, request, product_id):
        try:
            product = Product.objects.get(pk=product_id)
        except Product.DoesNotExist:
            return error_response('Product not found.', 'NOT_FOUND', status.HTTP_404_NOT_FOUND)
        if not request.user.is_staff and getattr(request.user, 'vendor_profile', None) != product.vendor:
            return error_response('Permission denied.', 'FORBIDDEN', status.HTTP_403_FORBIDDEN)
        serializer = ProductImageSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(product=product)
        ProductService.invalidate_product_cache(str(product_id))
        return success_response(serializer.data, 'Image uploaded successfully.', status.HTTP_201_CREATED)


class CategoryListView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        categories = ProductService.get_category_tree()
        serializer = CategorySerializer(
            [c for c in categories if c.parent_id is None], many=True
        )
        return Response(serializer.data)


class TagListView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        tags = Tag.objects.all().order_by('name')
        return Response(TagSerializer(tags, many=True).data)
