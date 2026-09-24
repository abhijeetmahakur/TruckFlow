from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from .core.views import index_view

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('truckflow_backend.core.urls')),
    path('', index_view, name='home'),
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.BASE_DIR / 'frontend')
