"""Top level URL configuration for crc_service_portal project."""

from django.contrib import admin
from django.urls import path, include
from django.views.generic import TemplateView

from apps.health.views import HealthCheckView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', TemplateView.as_view(template_name='index.html'), name='home'),
    path('health/', HealthCheckView.as_view(), name='health_check_custom'),
    path('alloc/', include('apps.allocations.urls', namespace='alloc')),
    path('auth/', include('apps.jwt.urls', namespace='jwt')),
    path('prod/', include('apps.research_products.urls', namespace='research_products')),
]
