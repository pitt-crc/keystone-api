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


class PublicationViewSet(viewsets.ModelViewSet):
    """JSON ViewSet for querying publication database records"""

    queryset = Publication.objects
    serializer_class = PublicationSerializer


class AllocationsView(TemplateView):
    """View for creating new allocation records"""

    template_name = 'allocations/allocations.html'


class ProposalsView(TemplateView):
    """View for creating new allocation records"""

    template_name = 'allocations/proposals.html'


class PublicationsView(TemplateView):
    """View for creating new allocation records"""

    template_name = 'allocations/publications.html'
