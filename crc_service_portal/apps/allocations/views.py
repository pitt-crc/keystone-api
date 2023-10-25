from django.views.generic import TemplateView
from rest_framework import viewsets

from .models import Allocation, Publication, ProjectProposal
from .serializers import AllocationSerializer, PublicationSerializer, ProjectProposalSerializer


class AllocationViewSet(viewsets.ModelViewSet):
    """A read-only JSON view for querying allocation database records"""

    queryset = Allocation.objects
    serializer_class = AllocationSerializer


class ProjectProposalViewSet(viewsets.ModelViewSet):
    """A read-only JSON view for querying project proposal database records"""

    queryset = ProjectProposal.objects
    serializer_class = ProjectProposalSerializer


class PublicationViewSet(viewsets.ModelViewSet):
    """A read-only JSON view for querying publication database records"""

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
