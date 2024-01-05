"""Application logic for rendering HTML templates and handling HTTP requests.

View objects handle the processing of incoming HTTP requests and return the
appropriately rendered HTML template or other HTTP response.
"""

from rest_framework import viewsets, permissions
from rest_framework.serializers import Serializer

from .models import *
from .serializers import *

__all__ = ['ResearchGroupViewSet', 'UserViewSet']


class UserViewSet(viewsets.ModelViewSet):
    """Manage user information for accounts stored in the application database.

    Changes made via these endpoints will not propagate into third party OAuth
    systems.
    """

    queryset = User.objects.all()
    permission_classes = [permissions.IsAuthenticated]

    def get_serializer_class(self) -> type[Serializer]:
        """
        Return the serializer instance that should be used for validating and
        deserializing input, and for serializing output.
        """

        if self.request.user.is_staff or self.request.user.is_superuser:
            return UserSerializer

        return UsernameSerializer


class ResearchGroupViewSet(viewsets.ModelViewSet):
    """Manage user research group membership."""

    queryset = ResearchGroup.objects.all()
    serializer_class = ResearchGroupSerializer
    permission_classes = [permissions.IsAuthenticated, permissions.IsAdminUser]
