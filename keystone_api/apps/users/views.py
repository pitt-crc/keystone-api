"""Application logic for rendering HTML templates and handling HTTP requests.

View objects handle the processing of incoming HTTP requests and return the
appropriately rendered HTML template or other HTTP response.
"""

from rest_framework import viewsets, permissions

from .models import *
from .serializers import *

__all__ = ['ResearchGroupViewSet', 'UserViewSet']


class UserViewSet(viewsets.ModelViewSet):
    """Manage user information for accounts stored in the application database.

    Changes made via these endpoints will not propagate into third party OAuth
    systems.
    """

    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]


class ResearchGroupViewSet(viewsets.ModelViewSet):
    """Manage user research group membership."""

    queryset = ResearchGroup.objects.all()
    serializer_class = ResearchGroupSerializer
    permission_classes = [permissions.IsAuthenticated, permissions.IsAdminUser]
