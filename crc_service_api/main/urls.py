"""Top level URL configuration for crc_service_api project."""

from django.contrib import admin
from django.urls import path, include
from django.views.generic import TemplateView

urlpatterns = [
    path('', TemplateView.as_view(template_name='index.html'), name='home'),
    path('admin/', admin.site.urls),
    path('allocations/', include('apps.allocations.urls', namespace='alloc')),
    path('authorization/', include('apps.authorization.urls', namespace='authorization')),
    path('docs/', include('apps.docs.urls', namespace='docs')),
    path('health/', include('apps.health.urls', namespace='health')),
    path('products/', include('apps.research_products.urls', namespace='research_products')),
]
