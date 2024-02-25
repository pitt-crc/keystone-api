"""Top level URL configuration."""

from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.http import HttpResponse
from django.urls import path, include

urlpatterns = [
    path('', lambda *args: HttpResponse(f"Keystone API Version {settings.VERSION}"), name='home'),
    path('version', lambda *args: HttpResponse(settings.VERSION), name='version'),

    path('admin/', admin.site.urls),
    path('allocations/', include('apps.allocations.urls', namespace='alloc')),
    path('audit/', include('apps.audit.urls', namespace='audit')),
    path('authentication/', include('apps.authentication.urls', namespace='authentication')),
    path('health/', include('apps.health.urls', namespace='health')),

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

if settings.DEBUG:
    urlpatterns.append(path('docs/', include('apps.docs.urls', namespace='docs')))
