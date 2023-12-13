"""Application logic for rendering HTML templates and handling HTTP requests.

View objects handle the processing of incoming HTTP requests and return the
appropriately rendered HTML template or other HTTP response.
"""

from apps.users.models import ResearchGroup
from rest_framework import viewsets, permissions

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

    serializer_class = AllocationSerializer
    filterset_fields = '__all__'

    def get_queryset(self) -> list[Allocation]:
        """Return a list of allocations for the currently authenticated user

        Admin users are returned a list of all allocations across all users.
        """

        if self.request.user.is_staff() or self.request.user.is_superuser():
            return Allocation.objects.all()

        research_groups = ResearchGroup.objects.groups_for_user(self.request.user)
        return Allocation.objects.filter(proposal__group__in=research_groups).all()


class ProposalViewSet(viewsets.ModelViewSet):
    """Manage project proposals submitted by users to request additional service unit allocations."""

    serializer_class = ProposalSerializer
    filterset_fields = '__all__'

    def get_queryset(self) -> list[Proposal]:
        """Return a list of proposals for the currently authenticated user

        Admin users are returned a list of all proposals across all users.
        """

        if self.request.user.is_staff() or self.request.user.is_superuser():
            return Proposal.objects.all()

        research_groups = ResearchGroup.objects.groups_for_user(self.request.user)
        return Proposal.objects.filter(group__in=research_groups).all()


class ProposalReviewViewSet(viewsets.ModelViewSet):
    """Manage project proposal reviews submitted by administrators."""

    serializer_class = ProposalReviewSerializer
    filterset_fields = '__all__'

    def get_queryset(self) -> list[Allocation]:
        """Return a list of proposal reviews for the currently authenticated user

        Admin users are returned a list of all records across all users.
        """

        if self.request.user.is_staff() or self.request.user.is_superuser():
            return ProposalReview.objects.all()

        research_groups = ResearchGroup.objects.groups_for_user(self.request.user)
        return ProposalReview.objects.filter(proposal__group__in=research_groups).all()
