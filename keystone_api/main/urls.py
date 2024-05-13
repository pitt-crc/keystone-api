"""Top level URL configuration."""

from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.http import HttpResponse
from django.urls import path, include

urlpatterns = [
    path('', lambda *args: HttpResponse(f"Keystone API Version {settings.VERSION}")),
    path('admin/', admin.site.urls),
    path('allocations/', include('apps.allocations.urls')),
    path('authentication/', include('apps.authentication.urls')),
    path('health/', include('apps.health.urls')),
    path('logs/', include('apps.logging.urls')),
    path('openapi/', include('apps.openapi.urls')),
    path('research/', include('apps.research_products.urls')),
    path('users/', include('apps.users.urls')),
    path('version/', lambda *args: HttpResponse(settings.VERSION)),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

print(urlpatterns)