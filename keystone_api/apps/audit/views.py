"""Application logic for rendering HTML templates and handling HTTP requests.

View objects handle the processing of incoming HTTP requests and return the
appropriately rendered HTML template or other HTTP response.
"""

from auditlog.models import LogEntry
from rest_framework import permissions, viewsets

from .serializers import *

__all__ = ['LogEntryViewSet']


class LogEntryViewSet(viewsets.ReadOnlyModelViewSet):
    """Fetch records from the application audit log"""

    queryset = LogEntry.objects.all()
    serializer_class = LogEntrySerializer
    permission_classes = [permissions.IsAuthenticated, permissions.IsAdminUser]
