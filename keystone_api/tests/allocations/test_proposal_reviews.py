"""Tests for the `proposals` endpoint"""

from rest_framework.test import APITestCase

from apps.allocations.models import *
from apps.allocations.serializers import *
from .base import BaseListTests


class List(BaseListTests, APITestCase):
    """Test fetching lists of records from the root of the API endpoint"""

    model = ProposalReview
    serializer = ProposalReviewSerializer
    endpoint = '/allocations/proposal-reviews/'
    fixtures = ["endpoint_testing_data"]
