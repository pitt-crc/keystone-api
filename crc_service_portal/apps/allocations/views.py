"""Application logic for rendering HTML templates and handling HTTP requests.

View objects handle the processing of incoming HTTP requests and return the
appropriately rendered HTML template or other HTTP response.
"""

from django.views.generic import TemplateView
from rest_framework import viewsets

from .serializers import *


class ClusterViewSet(viewsets.ReadOnlyModelViewSet):
    """Read-only JSON ViewSet for querying cluster database records"""

    queryset = Cluster.objects
    serializer_class = ClusterSerializer


class AllocationViewSet(viewsets.ModelViewSet):
    """JSON ViewSet for querying allocation database records"""

    queryset = Allocation.objects
    serializer_class = AllocationSerializer


class ProposalViewSet(viewsets.ModelViewSet):
    """JSON ViewSet for querying proposal database records"""

    queryset = Proposal.objects
    serializer_class = ProposalSerializer


class AllocationsView(TemplateView):
    """View for creating new allocation records"""

    template_name = 'allocations/allocations.html'
