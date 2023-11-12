"""Application logic for rendering HTML templates and handling HTTP requests.

View objects handle the processing of incoming HTTP requests and return the
appropriately rendered HTML template or other HTTP response.
"""

from rest_framework import viewsets

from .models import *
from .serializers import *

__all__ = ['PublicationViewSet', 'GrantViewSet']


class PublicationViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for querying cluster publication records"""

    queryset = Publication.objects.all()
    serializer_class = PublicationSerializer


class GrantViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for querying grant database records"""

    queryset = Grant.objects.all()
    serializer_class = GrantSerializer
