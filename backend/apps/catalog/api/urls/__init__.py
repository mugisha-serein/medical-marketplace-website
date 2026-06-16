from django.urls import path

from apps.catalog import views

urlpatterns = [
    path('products/', views.ProductListView.as_view(), name='product-list'),
    path('products/<slug:slug>/', views.ProductDetailView.as_view(), name='product-detail'),
    path('categories/', views.CategoryListView.as_view(), name='category-list'),
    path('tags/', views.TagListView.as_view(), name='tag-list'),
    path('vendor/products/', views.VendorProductListCreateView.as_view(), name='vendor-product-list'),
    path('vendor/products/<uuid:product_id>/', views.VendorProductDetailView.as_view(), name='vendor-product-detail'),
    path(
        'vendor/products/<uuid:product_id>/images/',
        views.ProductImageUploadView.as_view(),
        name='product-image-upload',
    ),
]
