"""Unit tests for the `AllocationRequestReview` class."""

from django.test import TestCase

from apps.allocations.models import AllocationRequest, AllocationRequestReview
from apps.users.models import ResearchGroup, User


class ResearchGroupInterface(TestCase):
    """Test the implementation of methods required by the `RGModelInterface`."""

    def setUp(self) -> None:
        """Create mock user records"""

        # Create a ResearchGroup instance
        self.user = User.objects.create_user(username='pi', password='foobar123!')
        self.research_group = ResearchGroup.objects.create(pi=self.user, name='Test Group')

        # Create an AllocationRequest instance linked to the ResearchGroup
        self.allocation_request = AllocationRequest.objects.create(
            title='Test Request',
            description='A test description',
            group=self.research_group
        )

        # Create an AllocationRequestReview instance linked to the AllocationRequest
        self.reviewer = User.objects.create_user(username='reviewer', password='foobar123!')
        self.allocation_request_review = AllocationRequestReview.objects.create(
            status=AllocationRequestReview.StatusChoices.APPROVED,
            request=self.allocation_request,
            reviewer=self.reviewer
        )

    def test_get_research_group(self):
        """Test the get_research_group method returns the correct ResearchGroup."""

        research_group = self.allocation_request_review.get_research_group()
        self.assertEqual(research_group, self.research_group)
