"""Tests for the `allocations` endpoint"""

from rest_framework.test import APITestCase

from apps.allocations.models import *
from apps.allocations.serializers import *
from keystone_api.tests.allocations.base import BaseListTests


class List(BaseListTests, APITestCase):
    """Test fetching lists of records from the root of the API endpoint"""

    model = Allocation
    serializer = AllocationSerializer
    endpoint = '/allocations/allocations/'
    fixtures = ["allocations_endpoint_testing.yaml"]
