from rest_framework import serializers
from .models import Category, Tag, Product, ProductImage


class CategorySerializer(serializers.ModelSerializer):
    children = serializers.SerializerMethodField()

    class Meta:
        model = Category
        fields = ['id', 'name', 'slug', 'description', 'image', 'parent', 'children']

    def get_children(self, obj):
        if hasattr(obj, '_prefetched_objects_cache') or obj.children.exists():
            return CategorySerializer(obj.children.filter(is_active=True), many=True).data
        return []


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ['id', 'name', 'slug']


class ProductImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductImage
        fields = ['id', 'image', 'alt_text', 'is_primary', 'order']


class ProductListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for list views."""
    primary_image = serializers.SerializerMethodField()
    category_name = serializers.CharField(source='category.name', read_only=True)
    vendor_name = serializers.CharField(source='vendor.company_name', read_only=True)
    in_stock = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = [
            'id', 'name', 'slug', 'sku', 'price', 'condition',
            'short_description', 'manufacturer', 'model_number',
            'category_name', 'vendor_name', 'primary_image',
            'is_featured', 'in_stock', 'created_at',
        ]

    def get_primary_image(self, obj):
        images = obj.images.all()
        primary = next((img for img in images if img.is_primary), None)
        if primary is None and images:
            primary = images[0]
        if primary:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(primary.image.url)
            return primary.image.url
        return None

    def get_in_stock(self, obj):
        if hasattr(obj, 'stock_record'):
            return obj.stock_record.quantity > 0
        return False


class ProductDetailSerializer(serializers.ModelSerializer):
    """Full serializer for detail views."""
    images = ProductImageSerializer(many=True, read_only=True)
    tags = TagSerializer(many=True, read_only=True)
    category = CategorySerializer(read_only=True)
    vendor = serializers.SerializerMethodField()
    stock_quantity = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = [
            'id', 'name', 'slug', 'sku', 'price', 'condition',
            'description', 'short_description', 'manufacturer',
            'model_number', 'specifications', 'category', 'tags',
            'vendor', 'images', 'is_featured', 'stock_quantity',
            'created_at', 'updated_at',
        ]

    def get_vendor(self, obj):
        v = obj.vendor
        return {
            'id': str(v.id),
            'company_name': v.company_name,
            'is_verified': v.is_verified,
            'website': v.website,
        }

    def get_stock_quantity(self, obj):
        if hasattr(obj, 'stock_record'):
            return obj.stock_record.quantity
        return 0


class ProductCreateUpdateSerializer(serializers.ModelSerializer):
    tag_ids = serializers.ListField(child=serializers.UUIDField(), required=False, write_only=True)

    class Meta:
        model = Product
        fields = [
            'name', 'sku', 'price', 'condition', 'description',
            'short_description', 'manufacturer', 'model_number',
            'specifications', 'category', 'tag_ids', 'is_active', 'is_featured',
        ]

    def validate_price(self, value):
        if value <= 0:
            raise serializers.ValidationError('Price must be greater than zero.')
        return value

    def create(self, validated_data):
        from .services import ProductService
        tag_ids = validated_data.pop('tag_ids', [])
        validated_data['vendor'] = self.context['request'].user.vendor_profile
        validated_data['slug'] = ProductService.generate_unique_slug(validated_data['name'])
        product = Product.objects.create(**validated_data)
        if tag_ids:
            product.tags.set(tag_ids)
        product.update_search_vector()
        return product

    def update(self, instance, validated_data):
        from .services import ProductService
        tag_ids = validated_data.pop('tag_ids', None)
        if 'name' in validated_data and validated_data['name'] != instance.name:
            validated_data['slug'] = ProductService.generate_unique_slug(
                validated_data['name'], instance_id=instance.pk
            )
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        if tag_ids is not None:
            instance.tags.set(tag_ids)
        instance.update_search_vector()
        ProductService.invalidate_product_cache(str(instance.pk))
        return instance