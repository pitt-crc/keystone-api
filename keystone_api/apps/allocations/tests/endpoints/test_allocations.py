"""Tests for the `allocations` endpoint"""

from rest_framework import status
from rest_framework.test import APITestCase

from apps.allocations.models import *
from apps.allocations.serializers import *
from apps.users.models import User

ENDPOINT = '/allocations/allocations/'


class List(APITestCase):
    """Test the fetching of bulk records from the root of the API endpoint

    API requests are submitted for user accounts with varying levels of privileges
    and the results are compared to the expected permissions model.
    """

    fixtures = ["test_allocations"]

    def assert_user_returns_allocations(self, user: User, allocations: list[Allocation]) -> None:
        """Login as the given user and assert the returned data matches a given list of allocations

        Args:
            user: The user object to authenticate ass
            allocations: The expected allocation data
        """

        self.client.force_authenticate(user=user)
        response = self.client.get(ENDPOINT)
        self.assertEqual(AllocationSerializer(allocations, many=True).data, response.data)
        self.client.logout()

    def test_anonymous_user_unauthorized(self) -> None:
        """Test unauthenticated users are returned a 401 status code"""

        self.assertEqual(self.client.get(ENDPOINT).status_code, status.HTTP_401_UNAUTHORIZED)

    def test_regular_user(self) -> None:
        """Test unprivileged users only have access to records they are affiliated with

        Tests are executed for multiple user account spanning different combinations of group memberships.
        """

        user1 = User.objects.get(username='user1')
        self.assert_user_returns_allocations(user1, Allocation.objects.affiliated_with_user(user1))

        user2 = User.objects.get(username='user2')
        self.assert_user_returns_allocations(user1, Allocation.objects.affiliated_with_user(user2))

        common_user = User.objects.get(username='common_user')
        self.assert_user_returns_allocations(common_user, Allocation.objects.affiliated_with_user(common_user))

    def test_staff_user(self) -> None:
        """Test staff users have access to all records in the database"""

        staff_user = User.objects.get(username='staff_user')
        self.assert_user_returns_allocations(staff_user, Allocation.objects.all())

    def test_super_user(self) -> None:
        """Test super-users have access to all records in the database"""

        super_user = User.objects.get(username='super_user')
        self.assert_user_returns_allocations(super_user, Allocation.objects.all())
