from django.urls import path

from apps.orders import views

urlpatterns = [
    path('vendor/', views.VendorOrderListView.as_view(), name='vendor-order-list'),
    path('', views.OrderListCreateView.as_view(), name='order-list-create'),
    path('<uuid:order_id>/', views.OrderDetailView.as_view(), name='order-detail'),
    path('<uuid:order_id>/transition/', views.OrderStatusTransitionView.as_view(), name='order-transition'),
]
