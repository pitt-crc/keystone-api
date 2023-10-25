from django.views import View
from django.views.generic import TemplateView
from rest_framework import viewsets

from .forms import AllocationForm
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


class AllocationView(TemplateView):
    """View for creating new allocation records"""

    template_name = 'allocations/allocations.html'
