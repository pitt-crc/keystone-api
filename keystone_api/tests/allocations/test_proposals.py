"""Tests for the `proposals` endpoint"""

from rest_framework.test import APITestCase

from apps.allocations.models import *
from apps.allocations.serializers import *
from .base import BaseListTests


class List(BaseListTests, APITestCase):
    """Test fetching lists of records from the root of the API endpoint"""

    model = Proposal
    serializer = ProposalSerializer
    endpoint = '/allocations/proposals/'
    fixtures = ["allocations_endpoint_testing.yaml"]
