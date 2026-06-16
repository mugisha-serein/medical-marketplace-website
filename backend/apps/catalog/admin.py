from django.contrib import admin
from .models import Category, Tag, Product, ProductImage


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'parent', 'is_active']
    prepopulated_fields = {'slug': ('name',)}
    list_filter = ['is_active', 'parent']


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug']
    prepopulated_fields = {'slug': ('name',)}


class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'sku', 'vendor', 'category', 'price', 'condition', 'is_active', 'is_featured']
    list_filter = ['is_active', 'is_featured', 'condition', 'category']
    search_fields = ['name', 'sku', 'manufacturer']
    prepopulated_fields = {'slug': ('name',)}
    inlines = [ProductImageInline]
    actions = ['rebuild_search_vectors']
    readonly_fields = ['created_at', 'updated_at']

    def rebuild_search_vectors(self, request, queryset):
        for product in queryset:
            product.update_search_vector()
        self.message_user(request, f'Rebuilt search vectors for {queryset.count()} products.')
    rebuild_search_vectors.short_description = 'Rebuild search vectors'