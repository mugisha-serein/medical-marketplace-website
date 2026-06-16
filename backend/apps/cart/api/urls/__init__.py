from django.urls import path

from apps.cart import views

urlpatterns = [
    path('', views.CartView.as_view(), name='cart'),
    path('items/', views.CartItemView.as_view(), name='cart-item-add'),
    path('items/<uuid:product_id>/', views.CartItemView.as_view(), name='cart-item-detail'),
]
