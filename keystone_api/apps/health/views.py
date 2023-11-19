"""Application logic for rendering HTML templates and handling HTTP requests.

View objects handle the processing of incoming HTTP requests and return the
appropriately rendered HTML template or other HTTP response.
"""

from django.core.handlers.wsgi import HttpRequest
from django.http import JsonResponse
from health_check.mixins import CheckMixin
from rest_framework.viewsets import ViewSet

__all__ = ['HealthCheckViewSet']


class HealthCheckViewSet(CheckMixin, ViewSet):
    """View for rendering system status messages"""

    def list(self, request: HttpRequest, *args, **kwargs) -> JsonResponse:
        """Return a JSON responses detailing system status checks

        Functions similarly to the overloaded parent method, except responses
        are forced to be JSON format and are never rendered HTML.
        """

        status_code = 500 if self.errors else 200
        return self.render_to_response_json(self.plugins, status_code)

    def render_to_response_json(self, plugins, status: int) -> JsonResponse:
        """Render a JSON response summarizing the status for a list of plugins

        Args:
            plugins: A list of plugins to render the status for
            status: THe overall system status

        Returns:
            A JSON HTTP response
        """

        data = dict()
        for plug in plugins:
            data[plug.identifier()] = {
                'status': 200 if plug.status else 500,
                'message': plug.pretty_status(),
                'time': plug.time_taken,
                'critical_service': plug.critical_service
            }

        return JsonResponse(data=data, status=status)
