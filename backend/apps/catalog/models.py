import uuid
from django.db import models


class Category(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255, unique=True)
    slug = models.SlugField(max_length=255, unique=True, db_index=True)
    parent = models.ForeignKey('self', null=True, blank=True, on_delete=models.SET_NULL, related_name='children')
    description = models.TextField(blank=True)
    image = models.ImageField(upload_to='category_images/', null=True, blank=True)
    is_active = models.BooleanField(default=True, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'catalog_category'
        verbose_name_plural = 'categories'
        ordering = ['name']

    def __str__(self):
        return self.name


class Tag(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=100, unique=True)

    class Meta:
        db_table = 'catalog_tag'
        ordering = ['name']

    def __str__(self):
        return self.name


class Product(models.Model):
    class Condition(models.TextChoices):
        NEW = 'new', 'New'
        REFURBISHED = 'refurbished', 'Refurbished'
        USED = 'used', 'Used'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    vendor = models.ForeignKey(
        'accounts.VendorProfile', on_delete=models.CASCADE, related_name='products'
    )
    category = models.ForeignKey(
        Category, on_delete=models.PROTECT, related_name='products'
    )
    tags = models.ManyToManyField(Tag, blank=True, related_name='products')

    name = models.CharField(max_length=500)
    slug = models.SlugField(max_length=500, unique=True, db_index=True)
    sku = models.CharField(max_length=100, unique=True, db_index=True)
    description = models.TextField()
    short_description = models.CharField(max_length=500, blank=True)

    price = models.DecimalField(max_digits=12, decimal_places=2)
    condition = models.CharField(max_length=20, choices=Condition.choices, default=Condition.NEW, db_index=True)
    manufacturer = models.CharField(max_length=255, blank=True)
    model_number = models.CharField(max_length=255, blank=True)
    specifications = models.JSONField(default=dict, blank=True)
    stock_quantity = models.PositiveIntegerField(default=0)

    is_active = models.BooleanField(default=True, db_index=True)
    is_featured = models.BooleanField(default=False, db_index=True)

    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'catalog_product'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['category', 'is_active', 'price'], name='product_category_active_price'),
            models.Index(fields=['vendor', 'is_active'], name='product_vendor_active'),
            models.Index(fields=['condition', 'is_active'], name='product_condition_active'),
            models.Index(fields=['-created_at'], name='product_created_desc'),
        ]

    def __str__(self):
        return self.name

    def update_search_vector(self):
        """SQLite MVP keeps simple icontains search in the service layer."""
        return None


class ProductImage(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='product_images/%Y/%m/')
    alt_text = models.CharField(max_length=255, blank=True)
    is_primary = models.BooleanField(default=False)
    order = models.PositiveSmallIntegerField(default=0)

    class Meta:
        db_table = 'catalog_product_image'
        ordering = ['order', 'id']

    def save(self, *args, **kwargs):
        if self.is_primary:
            ProductImage.objects.filter(product=self.product, is_primary=True).exclude(pk=self.pk).update(is_primary=False)
        super().save(*args, **kwargs)
