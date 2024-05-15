"""Application logic for rendering HTML templates and handling HTTP requests.

View objects handle the processing of incoming HTTP requests and return the
appropriately rendered HTML template or other HTTP response.
"""

from django.http import HttpResponse, JsonResponse
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from drf_spectacular.utils import extend_schema, inline_serializer
from health_check.mixins import CheckMixin
from rest_framework.generics import GenericAPIView

__all__ = ['HealthCheckView', 'HealthCheckJsonView', 'HealthCheckPrometheusView']


class HealthCheckView(GenericAPIView, CheckMixin):
    """Return a 200 status code if all health checks pass and 500 otherwise"""

    permission_classes = []

    @extend_schema(responses={
        '200': inline_serializer('OK', fields=dict()),
        '500': inline_serializer('Error', fields=dict()),
    })
    @method_decorator(cache_page(60))
    def get(self, request, *args, **kwargs) -> HttpResponse:
        """Return a status code reflecting the global status of system health checks."""

        self.check()

        for plugin in self.plugins.values():
            if plugin.status != 1:
                return HttpResponse(status=500)

        return HttpResponse()


class HealthCheckJsonView(GenericAPIView, CheckMixin):
    """Return system health checks in JSON format"""

    permission_classes = []

    @extend_schema(responses={
        '200': inline_serializer('OK', fields=dict()),
    })
    @method_decorator(cache_page(60))
    def get(self, request, *args, **kwargs) -> HttpResponse:
        """Summarize health checks in JSON format."""

        self.check()

        data = dict()
        for plugin_name, plugin in self.plugins.items():
            data[plugin_name] = {
                'status': 200 if plugin.status == 1 else 500,
                'message': plugin.pretty_status(),
                'critical_service': plugin.critical_service
            }

        return JsonResponse(data=data, status=200)


class HealthCheckPrometheusView(GenericAPIView, CheckMixin):
    """Return system health checks in Prometheus format"""

    permission_classes = []

    @extend_schema(responses={
        '200': inline_serializer('OK', fields=dict()),
    })
    @method_decorator(cache_page(60))
    def get(self, request, *args, **kwargs) -> HttpResponse:
        """Summarize health checks in Prometheus format."""

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
