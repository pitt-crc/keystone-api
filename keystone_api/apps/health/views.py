"""Application logic for rendering HTML templates and handling HTTP requests.

View objects handle the processing of incoming HTTP requests and return the
appropriately rendered HTML template or other HTTP response.
"""

from django.http import HttpResponse, JsonResponse
from health_check.mixins import CheckMixin
from rest_framework.views import APIView

__all__ = ['HealthCheckView', 'HealthCheckJsonView', 'HealthCheckPrometheusView']


class HealthCheckView(APIView, CheckMixin):
    """Return a 200 status code if all system checks pass and 500 otherwise"""

    permission_classes = []

    def get(self, request, *args, **kwargs) -> HttpResponse:
        """Return a 200 status code if all system checks pass and 500 otherwise

        Args:
            request: The incoming HTTP request

        Returns:
            An Http response
        """

        for plugin_name, plugin in self.plugins.items():
            plugin.check_status()
            if plugin.status != 1:
                return HttpResponse(status=500)

        return HttpResponse()


class HealthCheckJsonView(APIView, CheckMixin):
    """View for rendering system health checks in JSON format"""

    permission_classes = []

    def get(self, request, *args, **kwargs) -> JsonResponse:
        """Render a JSON response summarizing system health checks

        Args:
            request: The incoming HTTP request

        Returns:
            A JSON HTTP response
        """

        self.check()

        data = dict()
        for plugin_name, plugin in self.plugins.items():
            data[plugin_name] = {
                'status': 200 if plugin.status == 1 else 500,
                'message': plugin.pretty_status(),
                'critical_service': plugin.critical_service
            }

        return JsonResponse(data=data, status=200)


class HealthCheckPrometheusView(APIView, CheckMixin):
    """View for rendering system health checks in Prometheus format"""

    permission_classes = []

    def get(self, request, *args, **kwargs) -> HttpResponse:
        """Render an HTTP response summarizing system health checks

        Args:
            request: The incoming HTTP request

        Returns:
            An HTTP response
        """

        self.check()
        status_data = [
            '{name}{{critical_service="{critical_service}",message="{message}"}} {status:.1f}'.format(
                name=plugin_name,
                critical_service=plugin.critical_service,
                message=plugin.pretty_status(),
                status=200 if plugin.status else 500
            ) for plugin_name, plugin in self.plugins.items()
        ]

        return HttpResponse('\n'.join(status_data), status=200, content_type="text/plain")
