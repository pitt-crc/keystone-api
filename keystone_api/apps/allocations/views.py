"""Application logic for rendering HTML templates and handling HTTP requests.

View objects handle the processing of incoming HTTP requests and return the
appropriately rendered HTML template or other HTTP response.
"""

from rest_framework import viewsets

from .models import *
from .serializers import *

__all__ = ['AllocationViewSet', 'ClusterViewSet', 'ProposalViewSet']


class ClusterViewSet(viewsets.ReadOnlyModelViewSet):
    """Read-only JSON ViewSet for querying cluster database records"""

    queryset = Cluster.objects.all()
    serializer_class = ClusterSerializer


class AllocationViewSet(viewsets.ModelViewSet):
    """JSON ViewSet for querying allocation database records"""

    queryset = Allocation.objects.all()
    serializer_class = AllocationSerializer


class ProposalViewSet(viewsets.ModelViewSet):
    """JSON ViewSet for querying proposal database records"""

    queryset = Proposal.objects.all()
    serializer_class = ProposalSerializer
