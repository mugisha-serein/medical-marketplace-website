from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny

from .models import Product
from .serializers import ProductListSerializer, ProductDetailSerializer, CategorySerializer
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


class CategoryListView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        categories = ProductService.get_category_tree()
        serializer = CategorySerializer(
            [c for c in categories if c.parent_id is None], many=True
        )
        return Response(serializer.data)
