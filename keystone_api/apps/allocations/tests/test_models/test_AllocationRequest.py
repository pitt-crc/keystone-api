"""Unit tests for the `AllocationRequest` class."""
from datetime import date, timedelta

from django.core.exceptions import ValidationError
from django.test import TestCase

from apps.allocations.models import AllocationRequest
from apps.users.models import ResearchGroup, User


class ResearchGroupInterface(TestCase):
    """Test the implementation of methods required by the `RGModelInterface`."""

    def setUp(self) -> None:
        """Create mock user records"""

        self.user = User.objects.create_user(username='pi', password='foobar123!')
        self.research_group = ResearchGroup.objects.create(pi=self.user, name='Test Group')
        self.allocation_request = AllocationRequest.objects.create(
            title='Test Request',
            description='A test description',
            group=self.research_group
        )

    def test_get_research_group(self) -> None:
        """Test the get_research_group method returns the correct ResearchGroup."""

        research_group = self.allocation_request.get_research_group()
        self.assertEqual(research_group, self.research_group)


class Clean(TestCase):
    """Test the validation of record data."""

    def setUp(self) -> None:
        """Create mock user records"""

        self.user = User.objects.create_user(username='pi', password='foobar123!')
        self.research_group = ResearchGroup.objects.create(pi=self.user, name='Test Group')

    def test_clean_method_valid(self) -> None:
        """Test the clean method returns successfully when dates are valid."""

        allocation_request = AllocationRequest.objects.create(
            title='Test Request',
            description='A test description',
            group=self.research_group,
            active='2024-01-01',
            expire='2024-12-31'
        )

        allocation_request.clean()

    def test_clean_method_invalid(self) -> None:
        """Test the clean method raises a `ValidationError` when active date is after or equal to expire."""

        allocation_request_after = AllocationRequest.objects.create(
            title='Test Request',
            description='A test description',
            group=self.research_group,
            active='2024-12-31',
            expire='2024-01-01'
        )

        with self.assertRaises(ValidationError):
            allocation_request_after.clean()

        allocation_request_equal = AllocationRequest.objects.create(
            title='Test Request',
            description='A test description',
            group=self.research_group,
            active='2024-01-01',
            expire='2024-01-01'
        )

        with self.assertRaises(ValidationError):
            allocation_request_equal.clean()


class GetDaysUntilExpired(TestCase):
    """Test calculating the number of days until a request expires."""

    def setUp(self) -> None:
        """Set up test data."""

        self.user = User.objects.create_user(username='pi', password='foobar123!')
        self.research_group = ResearchGroup.objects.create(pi=self.user, name='Test Group')

    def test_future_date(self) -> None:
        """Test when the expiration date is in the future."""

        request = AllocationRequest.objects.create(
            title="Test Request",
            description="Test Description",
            expire=date.today() + timedelta(days=10),
            group=self.research_group
        )
        self.assertEqual(request.get_days_until_expire(), 10)

    def test_past_date(self) -> None:
        """Test when the expiration date is in the past."""

        request = AllocationRequest.objects.create(
            title="Test Request",
            description="Test Description",
            expire=date.today() - timedelta(days=5),
            group=self.research_group
        )
        self.assertEqual(request.get_days_until_expire(), -5)

    def test_today_date(self) -> None:
        """Test when the expiration date is today."""

        request = AllocationRequest.objects.create(
            title="Test Request",
            description="Test Description",
            expire=date.today(),
            group=self.research_group
        )
        self.assertEqual(request.get_days_until_expire(), 0)

    def test_none_date(self) -> None:
        """Test when the expiration date is `None`."""

        request = AllocationRequest.objects.create(
            title="Test Request",
            description="Test Description",
            expire=None,
            group=self.research_group
        )
        self.assertIsNone(request.get_days_until_expire())
