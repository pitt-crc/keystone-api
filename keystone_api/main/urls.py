"""Top level URL configuration."""

from django.conf import settings
from django.contrib import admin
from django.http import HttpResponse
from django.urls import path, include

urlpatterns = [
    path('', lambda *args: HttpResponse(f"Service Portal API Version {settings.VERSION}"), name='home'),
    path('admin/', admin.site.urls),
    path('allocations/', include('apps.allocations.urls', namespace='alloc')),
    path('audit/', include('apps.audit.urls', namespace='audit')),
    path('authentication/', include('apps.authentication.urls', namespace='authentication')),
    path('health/', include('apps.health.urls', namespace='health')),
    path('research-products/', include('apps.research_products.urls', namespace='research_products')),
]

if settings.DEBUG:
    urlpatterns.append(path('docs/', include('apps.docs.urls', namespace='docs')))
