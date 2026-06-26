"""Versioned API router for the SQLite MVP."""
from django.urls import path, include
from config.health import urlpatterns as health_urls

urlpatterns = [
    path('health/', include((health_urls, 'health'), namespace='health')),
    path('catalog/', include('apps.catalog.urls')),
    path('inquiries/', include('apps.inquiries.urls')),
]
