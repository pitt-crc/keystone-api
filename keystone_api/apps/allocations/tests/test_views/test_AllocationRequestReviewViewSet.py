"""Unit tests for the `AllocationRequestReviewViewSet` class."""

from django.test import RequestFactory, TestCase

from apps.allocations.models import AllocationRequestReview
from apps.allocations.views import AllocationRequestReviewViewSet
from apps.users.models import ResearchGroup, User


class GetQueryset(TestCase):
    """Test the generation of database queries based on user permissions."""

    def setUp(self) -> None:
        self.user1 = User.objects.create_user('user', 'foobar123!', is_staff=False)
        self.group1 = ResearchGroup.objects.create(name='group1', pi=self.user1)

        self.user2 = User.objects.create_user('user', 'foobar123!', is_staff=False)
        self.group1 = ResearchGroup.objects.create(name='group2', pi=self.user1)

        self.staff_user = User.objects.create_user('user', 'foobar123!', is_staff=False)

    def test_get_queryset_for_staff_user(self) -> None:
        """Test staff users can query all allocations."""

        request = RequestFactory()
        request.user = User.objects.get('general_user')

        viewset = AllocationRequestReviewViewSet()
        viewset.request = request

        queryset = viewset.get_queryset()
        self.assertEqual(queryset, AllocationRequestReview.objects.all())

    def test_get_queryset_for_non_staff_user(self) -> None:
        """Test non-staff users can only query allocations for their own research groups."""

        request = RequestFactory()
        request.user = User.objects.get('staff_user')

        viewset = AllocationRequestReviewViewSet()
        viewset.request = request

        queryset = viewset.get_queryset()
        self.assertEqual(queryset, AllocationRequestReview.objects.filter(request__group__in=[1, 2]))


class Create(TestCase):
    """Test the creation of new records."""

    def test_create_with_automatic_reviewer(self, ) -> None:
        """Test the reviewer field is automatically set to the current user."""

        self.fail()

    def test_create_with_provided_reviewer(self, ) -> None:
        """Test the reviewer field in the request data is respected if provided."""

        self.fail()
