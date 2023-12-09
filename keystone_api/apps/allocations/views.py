"""Application logic for rendering HTML templates and handling HTTP requests.

View objects handle the processing of incoming HTTP requests and return the
appropriately rendered HTML template or other HTTP response.
"""

from rest_framework import viewsets

from .models import *
from .serializers import *

__all__ = ['AllocationViewSet', 'ClusterViewSet', 'ProposalViewSet', 'ProposalReviewViewSet']


class ClusterViewSet(viewsets.ModelViewSet):
    """System settings and configuration for managed Slurm clusters."""

    queryset = Cluster.objects.all()
    serializer_class = ClusterSerializer
    filterset_fields = '__all__'


class AllocationViewSet(viewsets.ModelViewSet):
    """Manage SU allocations for user research groups."""

    queryset = Allocation.objects.all()
    serializer_class = AllocationSerializer
    filterset_fields = '__all__'


class ProposalViewSet(viewsets.ModelViewSet):
    """Manage project proposals used to request additional service unit allocations."""

    queryset = Proposal.objects.all()
    serializer_class = ProposalSerializer
    filterset_fields = '__all__'


class ProposalReviewViewSet(viewsets.ModelViewSet):
    """Manage project proposal reviews."""

    queryset = ProposalReview.objects.all()
    serializer_class = ProposalReviewSerializer
    filterset_fields = '__all__'
