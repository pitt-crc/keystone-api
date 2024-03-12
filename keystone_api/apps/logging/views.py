"""Application logic for rendering HTML templates and handling HTTP requests.

View objects handle the processing of incoming HTTP requests and return the
appropriately rendered HTML template or other HTTP response.
"""

from rest_framework import viewsets, permissions

from .models import *
from .serializers import *

__all__ = ['LogEntryViewSet']


class LogEntryViewSet(viewsets.ReadOnlyModelViewSet):
    """Returns application log data"""

    queryset = LogEntry.objects.all()
    serializer_class = LogEntrySerializer
    filterset_fields = '__all__'
    permission_classes = [permissions.IsAuthenticated, permissions.IsAdminUser]
