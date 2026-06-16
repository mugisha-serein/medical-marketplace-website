"""
Versioned API router — single entry for all MVP HTTP endpoints.

Mounted at: /api/v1/
"""
from django.urls import path, include
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView

urlpatterns = [
    path('auth/', include('apps.accounts.api.urls')),
    path('catalog/', include('apps.catalog.api.urls')),
    path('cart/', include('apps.cart.api.urls')),
    path('orders/', include('apps.orders.api.urls')),
    path('inventory/', include('apps.inventory.api.urls')),
    path('kpi/', include('apps.kpi.api.urls')),
    path('inquiries/', include('apps.inquiries.api.urls')),
    path('notifications/', include('apps.notification.api.urls')),
    path('health/', include('config.health')),
    path('schema/', SpectacularAPIView.as_view(), name='schema'),
    path('docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
]
