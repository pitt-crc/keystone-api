"""Application logic for rendering HTML templates and handling HTTP requests.

View objects handle the processing of incoming HTTP requests and return the
appropriately rendered HTML template or other HTTP response.
"""

from rest_framework import viewsets

from .models import *
from .permissions import *
from .serializers import *

__all__ = ['AllocationViewSet', 'ClusterViewSet', 'ProposalViewSet', 'ProposalReviewViewSet']


class ClusterViewSet(viewsets.ModelViewSet):
    """System settings and configuration for managed Slurm clusters."""

    permission_classes = [StaffWriteAuthenticatedRead]
    queryset = Cluster.objects.all()
    serializer_class = ClusterSerializer
    filterset_fields = '__all__'


class AllocationViewSet(viewsets.ModelViewSet):
    """Manage SU allocations for user research groups."""

    permission_classes = [StaffWriteGroupRead]
    serializer_class = AllocationSerializer
    filterset_fields = '__all__'

    def get_queryset(self) -> list[Allocation]:
        """Return a list of allocations for the currently authenticated user

        Admin users are returned a list of all allocations across all users.
        """

        if self.request.user.is_staff or self.request.user.is_superuser:
            return Allocation.objects.all()

        return Allocation.objects.affiliated_with_user(self.request.user).all()


class ProposalViewSet(viewsets.ModelViewSet):
    """Manage project proposals submitted by users to request additional service unit allocations."""

    serializer_class = ProposalSerializer
    filterset_fields = '__all__'

    def get_queryset(self) -> list[Proposal]:
        """Return a list of proposals for the currently authenticated user

        Admin users are returned a list of all proposals across all users.
        """

        if self.request.user.is_staff or self.request.user.is_superuser:
            return Proposal.objects.all()

        return Proposal.objects.affiliated_with_user(self.request.user).all()


class ProposalReviewViewSet(viewsets.ModelViewSet):
    """Manage project proposal reviews submitted by administrators."""

    serializer_class = ProposalReviewSerializer
    filterset_fields = '__all__'

    def get_queryset(self) -> list[Allocation]:
        """Return a list of proposal reviews for the currently authenticated user

        Admin users are returned a list of all records across all users.
        """

        if self.request.user.is_staff or self.request.user.is_superuser:
            return ProposalReview.objects.all()

        return ProposalReview.objects.affiliated_with_user(self.request.user).all()
