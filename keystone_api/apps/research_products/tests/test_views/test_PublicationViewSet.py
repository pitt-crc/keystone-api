"""Unit tests for the `PublicationViewSet` class."""

from django.contrib.auth import get_user_model
from django.test import TestCase

from apps.research_products.models import Publication
from apps.research_products.views import PublicationViewSet
from apps.users.models import ResearchGroup

User = get_user_model()


class GetQueryset(TestCase):
    """Test the filtering of records based on user status."""

    def setUp(self) -> None:
        """Create user accounts and research publications."""

        self.staff_user = User.objects.create_user(username='staff', password='foobar123!', is_staff=True)
        self.general_user = User.objects.create_user(username='general', password='foobar123!')

        self.group1_user = User.objects.create_user(username='user1', password='foobar123!')
        self.group1 = ResearchGroup.objects.create(name='Group1', pi=self.group1_user)
        self.group1_publication = Publication.objects.create(
            title="Publication 1",
            abstract="Abstract 1",
            date="2020-01-01",
            journal="Journal 1",
            group=self.group1
        )

        self.group2_user = User.objects.create_user(username='user2', password='foobar123!')
        self.group2 = ResearchGroup.objects.create(name='Group2', pi=self.group2_user)
        self.group2_publication = Publication.objects.create(
            title="Publication 2",
            abstract="Abstract 2",
            date="2020-01-02",
            journal="Journal 2",
            group=self.group2
        )

    def create_viewset(self, user: User) -> PublicationViewSet:
        """Create a viewset for testing purposes.

        Args:
            user: The user submitting a request to the viewset.

        Returns:
            A viewset instance tied to a request from the given user.
        """

        viewset = PublicationViewSet()
        viewset.request = self.client.request().wsgi_request
        viewset.request.user = user
        return viewset

    def test_queryset_for_staff_user(self) -> None:
        """Test staff users can view all publications."""

        viewset = self.create_viewset(self.staff_user)
        queryset = viewset.get_queryset()
        self.assertEqual(len(queryset), 2)

    def test_queryset_for_group_member(self) -> None:
        """Test user's can only access their group's publications."""

        viewset = self.create_viewset(self.group1_user)
        queryset = viewset.get_queryset()
        self.assertEqual(len(queryset), 1)
        self.assertEqual(queryset[0].group, self.group1)

    def test_queryset_for_non_group_member(self) -> None:
        """Test user's without groups cannot access any records."""

        viewset = self.create_viewset(self.general_user)
        queryset = viewset.get_queryset()
        self.assertEqual(len(queryset), 0)
