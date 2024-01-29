"""Application logic for rendering HTML templates and handling HTTP requests.

View objects handle the processing of incoming HTTP requests and return the
appropriately rendered HTML template or other HTTP response.
"""

from rest_framework import permissions, serializers, status, viewsets
from rest_framework.response import Response

from .models import *
from .permissions import *
from .serializers import *

__all__ = ['AllocationViewSet', 'ClusterViewSet', 'ProposalViewSet', 'ProposalReviewViewSet']


class ClusterViewSet(viewsets.ModelViewSet):
    """System settings and configuration for managed Slurm clusters."""

    permission_classes = [permissions.IsAuthenticated, StaffWriteAuthenticatedRead]
    queryset = Cluster.objects.all()
    filterset_fields = '__all__'

    def get_serializer_class(self) -> type[serializers.Serializer]:
        """Return the class to use for the serializer"""

        user = self.request.user
        if user.is_staff or user.is_superuser:
            return ClusterSerializer

        return SafeClusterSerializer


class AllocationViewSet(viewsets.ModelViewSet):
    """Manage SU allocations for user research groups."""

    permission_classes = [permissions.IsAuthenticated, StaffWriteGroupRead]
    serializer_class = AllocationSerializer
    filterset_fields = '__all__'

    def get_queryset(self) -> list[Allocation]:
        """Return a list of allocations for the currently authenticated user"""

        if self.request.user.is_staff or self.request.user.is_superuser:
            return Allocation.objects.all()

        return Allocation.objects.affiliated_with_user(self.request.user).all()


class ProposalViewSet(viewsets.ModelViewSet):
    """Manage project proposals submitted by users to request additional service unit allocations."""

    permission_classes = [permissions.IsAuthenticated, GroupAdminCreateGroupRead]
    serializer_class = ProposalSerializer
    filterset_fields = '__all__'

    def get_queryset(self) -> list[Proposal]:
        """Return a list of proposals for the currently authenticated user"""

        if self.request.user.is_staff or self.request.user.is_superuser:
            return Proposal.objects.all()

        return Proposal.objects.affiliated_with_user(self.request.user).all()


class ProposalReviewViewSet(viewsets.ModelViewSet):
    """Manage project proposal reviews submitted by administrators."""

    permission_classes = [permissions.IsAuthenticated, StaffWriteGroupRead]
    serializer_class = ProposalReviewSerializer
    filterset_fields = '__all__'

    def get_queryset(self) -> list[Allocation]:
        """Return a list of proposal reviews for the currently authenticated user"""

        if self.request.user.is_staff or self.request.user.is_superuser:
            return ProposalReview.objects.all()

        return ProposalReview.objects.affiliated_with_user(self.request.user).all()

    def create(self, request, *args, **kwargs) -> Response:
        """Create a new `ProposalReview` object"""

        data = request.data.copy()
        data.setdefault('reviewer', request.user.pk)

        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)

        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
