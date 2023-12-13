"""Tests for the `clusters` endpoint"""

from rest_framework import status
from rest_framework.test import APITestCase

from apps.allocations.models import *
from apps.allocations.serializers import *
from apps.users.models import User

ENDPOINT = '/allocations/clusters/'


class List(APITestCase):
    """Test fetching bulk records from the root of the API endpoint"""

    fixtures = ["endpoint_testing_data"]

    def test_anonymous_user_unauthorized(self) -> None:
        """Test unauthenticated users are returned a 401 status code"""

        self.assertEqual(self.client.get(ENDPOINT).status_code, status.HTTP_401_UNAUTHORIZED)

    def test_authenticated_users(self) -> None:
        """Test cluster data is available to all authenticated users"""

        # Run the test for user accounts with varying levels of permissions
        for username in ('common_user', 'staff_user', 'super_user'):
            user = User.objects.get(username=username)
            self.client.force_authenticate(user=user)

            expected_records = Cluster.objects.all()
            response = self.client.get(ENDPOINT)
            self.assertEqual(ClusterSerializer(expected_records, many=True).data, response.data)
