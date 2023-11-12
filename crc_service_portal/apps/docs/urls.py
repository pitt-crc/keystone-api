"""URL routing for the parent application"""

from django.urls import path
from django.views.generic import TemplateView
from rest_framework.schemas import get_schema_view

app_name = 'docs'

urlpatterns = [
    path('openapi', get_schema_view(
        title="Your Project",
        description="API for all things …",
        version="1.0.0"
    ), name='openapi-schema'),

    # This entry assumes the application is installed under the namespace `docs`
    path('', TemplateView.as_view(
        template_name='api_docs/redoc.html',
        extra_context={'schema_url': 'docs:openapi-schema'}
    ), name='redoc'),
]
