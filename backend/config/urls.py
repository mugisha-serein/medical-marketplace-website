from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/v1/', include('config.api.v1.urls')),
    # Backward-compatible public aliases used by older frontend code.
    path('api/catalog/', include('apps.catalog.urls')),
    path('api/inquiries/', include('apps.inquiries.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
