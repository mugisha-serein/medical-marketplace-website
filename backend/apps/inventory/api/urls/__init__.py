from django.urls import path

from apps.inventory import views

urlpatterns = [
    path(
        '<uuid:product_id>/stock/',
        views.StockDetailView.as_view(),
        name='inventory-stock',
    ),
    path(
        '<uuid:product_id>/stock/restock/',
        views.RestockView.as_view(),
        name='inventory-restock',
    ),
    path(
        '<uuid:product_id>/stock/movements/',
        views.StockMovementListView.as_view(),
        name='inventory-movements',
    ),
]
