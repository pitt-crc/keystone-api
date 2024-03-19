"""Application logic for rendering HTML templates and handling HTTP requests.

View objects handle the processing of incoming HTTP requests and return the
appropriately rendered HTML template or other HTTP response.
"""

from rest_framework import permissions, viewsets

from .models import *
from .serializers import *

__all__ = [
    'ResearchGroupViewSet',
    'UserViewSet',
]


class ResearchGroupViewSet(viewsets.ModelViewSet):
    """View or create ResearchGroups."""

    permission_classes = [permissions.IsAdminUser]
    serializer_class = ResearchGroupSerializer
    filterset_fields = '__all__'


class UserViewSet(viewsets.ModelViewSet):
    """View Users."""

    permission_classes = [permissions.IsAuthenticated]
    serializer_class = UserSerializer
    filterset_fields = '__all__'

    def get_queryset(self) -> list[User]:
        """Return a list of research groups for the currently authenticated user"""

        return User.objects.all()
