"""Versioned API router for the SQLite MVP."""
from django.urls import path, include

urlpatterns = [
    path('health/', include('config.health')),
    path('catalog/', include('apps.catalog.urls')),
    path('inquiries/', include('apps.inquiries.urls')),
]
