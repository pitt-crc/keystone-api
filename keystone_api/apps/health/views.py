"""Application logic for rendering HTML templates and handling HTTP requests.

View objects handle the processing of incoming HTTP requests and return the
appropriately rendered HTML template or other HTTP response.
"""

import abc

from django.http import HttpResponse, JsonResponse
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from health_check.mixins import CheckMixin
from rest_framework.views import APIView

__all__ = ['HealthCheckView', 'HealthCheckJsonView', 'HealthCheckPrometheusView']


class BaseView(APIView, CheckMixin, metaclass=abc.ABCMeta):
    """Base class that caches successful health check requests for one minute"""

    @staticmethod
    @abc.abstractmethod
    def render_response(plugins: dict) -> HttpResponse:
        """Summarize a list of health checks in an HTTP response"""

    @method_decorator(cache_page(60))
    def get(self, request, *args, **kwargs) -> HttpResponse:
        """Render system health checks into an HTTP response

        Args:
            request: The incoming HTTP request

        Returns:
            An Http response
        """

        self.check()
        return self.render_response(self.plugins)


class HealthCheckView(BaseView):
    """Return a 200 status code if all health checks pass and 500 otherwise"""

    permission_classes = []

    @staticmethod
    def render_response(plugins: dict) -> HttpResponse:
        """Return an HTTP response with a status code matching system health checks

        Args:
            plugins: A mapping of healthcheck names to health check objects

        Returns:
            An HTTPResponse with status 200 if all checks are passing or 500 otherwise
        """

        for plugin in plugins.values():
            if plugin.status != 1:
                return HttpResponse(status=500)

        return HttpResponse()


class HealthCheckJsonView(BaseView):
    """Return system health checks in JSON format"""

    permission_classes = []

    @staticmethod
    def render_response(plugins: dict) -> JsonResponse:
        """Return a JSON response summarizing a collection of health checks

        Args:
            plugins: A mapping of healthcheck names to health check objects

        Returns:
            A JSON response
        """

        data = dict()
        for plugin_name, plugin in plugins.items():
            data[plugin_name] = {
                'status': 200 if plugin.status == 1 else 500,
                'message': plugin.pretty_status(),
                'critical_service': plugin.critical_service
            }

        return JsonResponse(data=data, status=200)


class HealthCheckPrometheusView(BaseView):
    """Return system health checks in Prometheus format"""

    permission_classes = []

    @staticmethod
    def render_response(plugins: dict) -> HttpResponse:
        """Return an HTTP response summarizing a collection of health checks

        Args:
            plugins: A mapping of healthcheck names to health check objects

        Returns:
            An HTTP response
        """

        status_data = [
            '{name}{{critical_service="{critical_service}",message="{message}"}} {status:.1f}'.format(
                name=plugin_name,
                critical_service=plugin.critical_service,
                message=plugin.pretty_status(),
                status=200 if plugin.status else 500
            ) for plugin_name, plugin in plugins.items()
        ]
        return HttpResponse('\n'.join(status_data), status=200, content_type="text/plain")
