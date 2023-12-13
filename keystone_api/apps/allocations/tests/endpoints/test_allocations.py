"""Tests for the `allocations` endpoint"""

from rest_framework import status
from rest_framework.test import APITestCase

from apps.allocations.models import *
from apps.allocations.serializers import *
from apps.users.models import User

ENDPOINT = '/allocations/allocations/'


class List(APITestCase):
    """Test fetching bulk records from the root of the API endpoint"""

    fixtures = ["endpoint_testing_data"]

    def test_anonymous_user_unauthorized(self) -> None:
        """Test unauthenticated users are returned a 401 status code"""

        self.assertEqual(self.client.get(ENDPOINT).status_code, status.HTTP_401_UNAUTHORIZED)

    def test_regular_user(self) -> None:
        """Test unprivileged users only have access to records they are affiliated with

        Tests are executed for multiple user account spanning different combinations of group memberships.
        """

        for username in ('user1', 'user2', 'common_user'):
            user = User.objects.get(username=username)
            self.client.force_authenticate(user=user)

            expected_records = Allocation.objects.affiliated_with_user(user).all()
            response = self.client.get(ENDPOINT)
            self.assertEqual(AllocationSerializer(expected_records, many=True).data, response.data)

    def test_staff_user(self) -> None:
        """Test staff users have access to all records in the database"""

        staff_user = User.objects.get(username='staff_user')
        self.client.force_authenticate(user=staff_user)

        expected_records = Allocation.objects.all()
        expected_data = AllocationSerializer(expected_records, many=True).data
        self.assertEqual(expected_data, self.client.get(ENDPOINT).data)

    def test_super_user(self) -> None:
        """Test super-users have access to all records in the database"""

        super_user = User.objects.get(username='super_user')
        self.client.force_authenticate(user=super_user)

        expected_records = Allocation.objects.all()
        expected_data = AllocationSerializer(expected_records, many=True).data
        self.assertEqual(expected_data, self.client.get(ENDPOINT).data)
