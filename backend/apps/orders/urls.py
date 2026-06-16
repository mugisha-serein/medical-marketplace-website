from django.urls import path
from . import views

urlpatterns = [
    path('add/', views.OrderListCreateView.as_view(), name='place_order'),
    path('<int:order_id>/', views.OrderDetailView.as_view(), name='order_detail'),
]