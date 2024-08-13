"""Unit tests for the `Allocation` class."""

from django.test import TestCase

from apps.allocations.models import Allocation, AllocationRequest, Cluster
from apps.users.models import ResearchGroup, User


class ResearchGroupInterface(TestCase):
    """Test the implementation of methods required by the `RGModelInterface`."""

    def setUp(self) -> None:
        """Create mock user records"""

        self.user = User.objects.create_user(username='pi', password='foobar123!')
        self.research_group = ResearchGroup.objects.create(pi=self.user, name='Test Group')
        self.cluster = Cluster.objects.create(name='Test Cluster')
        self.allocation_request = AllocationRequest.objects.create(group=self.research_group)
        self.allocation = Allocation.objects.create(
            requested=100,
            cluster=self.cluster,
            request=self.allocation_request
        )

    def test_get_research_group(self) -> None:
        """Test the `get_research_group` method returns the correct ResearchGroup."""

        research_group = self.allocation.get_research_group()
        self.assertEqual(research_group, self.research_group)
