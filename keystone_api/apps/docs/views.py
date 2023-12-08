"""Application logic for rendering HTML templates and handling HTTP requests.

View objects handle the processing of incoming HTTP requests and return the
appropriately rendered HTML template or other HTTP response.
"""

from django.conf import settings
from django.views.generic import TemplateView
from rest_framework.schemas import get_schema_view

__all__ = ['RedocView', 'SchemaView']

SchemaView = get_schema_view(
    title="CRC Self Service API",
    description="A REST API for managing user resource allocations on HPC systems.",
    version=settings.VERSION,
    permission_classes=[],
    public=True
)


class RedocView(TemplateView):
    """View for rendering API documentation using Redoc"""

    # The `schema_url` assumes the application is installed under the namespace `docs`
    extra_context = {'schema_url': 'docs:openapi-schema'}
    template_name = 'redoc.html'
