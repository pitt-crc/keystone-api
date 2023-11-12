"""Top level URL configuration for crc_service_portal project."""

from django.contrib import admin
from django.urls import path, include
from django.views.generic import TemplateView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', TemplateView.as_view(template_name='index.html'), name='home'),
    path('health/', include('apps.health.urls', namespace='docs')),
    path('docs/', include('apps.docs.urls', namespace='docs')),
    path('auth/', include('apps.jwt.urls', namespace='jwt')),
    path('allocations/', include('apps.allocations.urls', namespace='alloc')),
    path('products/', include('apps.research_products.urls', namespace='research_products')),
]
