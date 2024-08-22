"""Unit tests for the `AllocationRequestReviewViewSet` class."""

from django.test import RequestFactory, TestCase
from rest_framework import status

from apps.allocations.models import AllocationRequest, AllocationRequestReview
from apps.allocations.views import AllocationRequestReviewViewSet
from apps.users.models import ResearchGroup, User


class GetQueryset(TestCase):
    """Test the filtering of database records based on user permissions."""

    fixtures = ['fixtures.yaml']

    def test_get_queryset_for_staff_user(self) -> None:
        """Test staff users can query all reviews."""

        request = RequestFactory()
        request.user = User.objects.get(username='staff')

        viewset = AllocationRequestReviewViewSet()
        viewset.request = request

        expected_queryset = AllocationRequestReview.objects.all()
        self.assertQuerysetEqual(expected_queryset, viewset.get_queryset(), ordered=False)

    def test_get_queryset_for_non_staff_user(self) -> None:
        """Test non-staff users can only query reviews for their own research groups."""

        request = RequestFactory()
        request.user = User.objects.get(username='user1')

        viewset = AllocationRequestReviewViewSet()
        viewset.request = request

        group1 = ResearchGroup.objects.get(name='group1')
        expected_queryset = AllocationRequestReview.objects.filter(request__group__in=[group1.id])
        self.assertQuerysetEqual(expected_queryset, viewset.get_queryset(), ordered=False)


class Create(TestCase):
    """Test the creation of new records."""

    # TODO: Move into fixture
    def setUp(self) -> None:
        self.staff_user = User.objects.create_user('staff', 'foobar123!', is_staff=True)

        self.user1 = User.objects.create_user('user1', 'foobar123!', is_staff=False)
        self.group1 = ResearchGroup.objects.create(name='group1', pi=self.user1)
        self.request1 = AllocationRequest.objects.create(title='request1', group=self.group1)

    def test_create_with_automatic_reviewer(self) -> None:
        """Test the reviewer field is automatically set to the current user."""

        request = RequestFactory().post('/allocation-reviews/')
        request.user = self.staff_user
        request.data = {
            'request': self.request1.id,
            'status': 'AP'
        }

        viewset = AllocationRequestReviewViewSet()
        viewset.request = request
        viewset.format_kwarg = None

        # Test the returned response data
        response = viewset.create(request)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['reviewer'], self.staff_user.id)

        # Test the created DB record
        review = AllocationRequestReview.objects.get(pk=response.data['id'])
        self.assertEqual(review.reviewer, self.staff_user)
        self.assertEqual(review.request, self.request1)
        self.assertEqual(review.status, 'AP')

    def test_create_with_provided_reviewer(self) -> None:
        """Test the reviewer field in the request data is respected if provided."""

        request = RequestFactory().post('/allocation-reviews/')
        request.user = self.staff_user
        request.data = {
            'request': self.request1.id,
            'reviewer': self.staff_user.id,
            'status': 'AP'
        }

        viewset = AllocationRequestReviewViewSet()
        viewset.request = request
        viewset.format_kwarg = None

        # Test the returned response data
        response = viewset.create(request)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['reviewer'], self.staff_user.id)

        # Test the created DB record
        review = AllocationRequestReview.objects.get(pk=response.data['id'])
        self.assertEqual(review.reviewer, self.staff_user)
        self.assertEqual(review.request, self.request1)
        self.assertEqual(review.status, 'AP')
