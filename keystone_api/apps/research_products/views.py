"""Application logic for rendering HTML templates and handling HTTP requests.

View objects handle the processing of incoming HTTP requests and return the
appropriately rendered HTML template or other HTTP response.
"""

from rest_framework import permissions, viewsets

from .models import *
from .permissions import *
from .serializers import *

__all__ = ['GrantViewSet', 'PublicationViewSet']


class PublicationViewSet(viewsets.ModelViewSet):
    """Manage metadata for research publications."""

    queryset = Publication.objects.all()
    permission_classes = [permissions.IsAuthenticated, permissions.IsAdminUser | GroupMemberAll]
    serializer_class = PublicationSerializer
    filterset_fields = '__all__'


class GrantViewSet(viewsets.ModelViewSet):
    """Track funding awards and grant information."""

    queryset = Grant.objects.all()
    permission_classes = [permissions.IsAuthenticated, permissions.IsAdminUser | GroupMemberReadGroupAdminWrite]
    serializer_class = GrantSerializer
    filterset_fields = '__all__'
