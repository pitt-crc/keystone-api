"""Tests for the `allocations` endpoint"""

from rest_framework import status
from rest_framework.test import APITestCase

from apps.users.models import User


class ListEndpointPermissions(APITestCase):
    """Test user permissions for the `/allocations/allocations/` endpoint

    Endpoint permissions are tested against the following matrix of HTTP responses.
    All listed responses assume the associated HTTP request is otherwise valid.

    | Authentication      | GET | HEAD | POST | PUT | PATCH | DELETE | OPTIONS | TRACE |
    |---------------------|-----|------|------|-----|-------|--------|---------|-------|
    | Anonymous User      | 401 | 401  | 401  | 401 | 401   | 401    | 401     | 401   |
    | Authenticated User  | 200 | 200  | 401  | 405 | 405   | 401    | 200     | 405   |
    | Staff User          | 200 | 200  | 201  | 405 | 405   | 405    | 200     | 405   |
    """

    endpoint = '/allocations/allocations/'
    valid_post_data = {'sus': 1000, 'cluster': 1, 'proposal': 1}
    fixtures = ['allocations_endpoint_testing.yaml']

    def test_anonymous_user_permissions(self) -> None:
        """Test unauthenticated users are returned a 401 status code for all request types"""

        self.assertEqual(self.client.get(self.endpoint).status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(self.client.head(self.endpoint).status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(self.client.post(self.endpoint).status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(self.client.put(self.endpoint).status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(self.client.patch(self.endpoint).status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(self.client.delete(self.endpoint).status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(self.client.options(self.endpoint).status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(self.client.trace(self.endpoint).status_code, status.HTTP_401_UNAUTHORIZED)

    def test_authenticated_user_permissions(self) -> None:
        """Test general authenticated users have read-only permissions"""

        user = User.objects.get(username='common_user')
        self.client.force_authenticate(user=user)

        # Allowed operations
        self.assertEqual(self.client.get(self.endpoint).status_code, status.HTTP_200_OK)
        self.assertEqual(self.client.head(self.endpoint).status_code, status.HTTP_200_OK)
        self.assertEqual(self.client.options(self.endpoint).status_code, status.HTTP_200_OK)

        # Unauthorized operations
        self.assertEqual(self.client.post(self.endpoint).status_code, status.HTTP_401_UNAUTHORIZED)

        # Disallowed operations
        self.assertEqual(self.client.put(self.endpoint).status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
        self.assertEqual(self.client.patch(self.endpoint).status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
        self.assertEqual(self.client.trace(self.endpoint).status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_staff_user_permissions(self) -> None:
        """Test staff users have read and write permissions"""

        user = User.objects.get(username='staff_user')
        self.client.force_authenticate(user=user)

        # Allowed operations
        self.assertEqual(self.client.get(self.endpoint).status_code, status.HTTP_200_OK)
        self.assertEqual(self.client.head(self.endpoint).status_code, status.HTTP_200_OK)
        self.assertEqual(self.client.options(self.endpoint).status_code, status.HTTP_200_OK)

        post = self.client.post(self.endpoint, data=self.valid_post_data)
        self.assertEqual(post.status_code, status.HTTP_201_CREATED)

        # Disallowed operations
        self.assertEqual(self.client.put(self.endpoint).status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
        self.assertEqual(self.client.patch(self.endpoint).status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
        self.assertEqual(self.client.trace(self.endpoint).status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
