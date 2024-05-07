"""Application logic for rendering HTML templates and handling HTTP requests.

View objects handle the processing of incoming HTTP requests and return the
appropriately rendered HTML template or other HTTP response.
"""

from rest_framework import permissions, viewsets

from .models import *
from .serializers import *

__all__ = ['AppLogViewSet', 'RequestLogViewSet', 'TaskResultViewSet']


class AppLogViewSet(viewsets.ReadOnlyModelViewSet):
    """Returns application log data"""

    queryset = AppLog.objects.all()
    serializer_class = AppLogSerializer
    filterset_fields = '__all__'
    permission_classes = [permissions.IsAuthenticated, permissions.IsAdminUser]


class RequestLogViewSet(viewsets.ReadOnlyModelViewSet):
    """Returns HTTP request log data"""

    queryset = RequestLog.objects.all()
    serializer_class = RequestLogSerializer
    filterset_fields = '__all__'
    permission_classes = [permissions.IsAuthenticated, permissions.IsAdminUser]


class TaskResultViewSet(viewsets.ReadOnlyModelViewSet):
    """Returns results from scheduled background tasks"""

    queryset = TaskResult.objects.all()
    serializer_class = TaskResultSerializer
    filterset_fields = '__all__'
    permission_classes = [permissions.IsAuthenticated, permissions.IsAdminUser]
