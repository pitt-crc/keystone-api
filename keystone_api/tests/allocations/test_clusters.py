"""Tests for the `clusters` endpoint"""

from rest_framework import status
from rest_framework.test import APITestCase

from apps.users.models import User


class ListEndpointPermissions(APITestCase):
    """Test user permissions against the `/allocations/clusters/` endpoint

    Endpoint permissions are tested against the following matrix of HTTP responses.
    All listed responses assume the associated HTTP request is otherwise valid.

    | Authentication      | GET | HEAD | POST | PUT | PATCH | DELETE | OPTIONS | TRACE |
    |---------------------|-----|------|------|-----|-------|--------|---------|-------|
    | Anonymous User      | 401 | 401  | 401  | 401 | 401   | 401    | 401     | 401   |
    | Authenticated User  | 200 | 200  | 401  | 405 | 405   | 401    | 200     | 405   |
    | Staff User          | 200 | 200  | 201  | 405 | 405   | 405    | 200     | 405   |
    """

    endpoint = '/allocations/clusters/'
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

        post = self.client.post(self.endpoint, data={'name': 'foo'})
        self.assertEqual(post.status_code, status.HTTP_201_CREATED)

        # Disallowed operations
        self.assertEqual(self.client.put(self.endpoint).status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
        self.assertEqual(self.client.patch(self.endpoint).status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
        self.assertEqual(self.client.trace(self.endpoint).status_code, status.HTTP_405_METHOD_NOT_ALLOWED)


class RecordEndpointPermissions(APITestCase):
    """Test user permissions against the `/allocations/clusters/` endpoint

    Endpoint permissions are tested against the following matrix of HTTP responses.
    All listed responses assume the associated HTTP request is otherwise valid.

    | Authentication      | GET | HEAD | POST | PUT | PATCH | DELETE | OPTIONS | TRACE |
    |---------------------|-----|------|------|-----|-------|--------|---------|-------|
    | Anonymous User      | 401 | 401  | 401  | 401 | 401   | 401    | 401     | 401   |
    | Authenticated User  | 200 | 200  | 405  | 403 | 403   | 405    | 200     | 405   |
    | Staff User          | 200 | 200  | 405  | 200 | 200   | 405    | 200     | 405   |
    """

    endpoint = '/allocations/clusters/{pk}/'
    fixtures = ['allocations_endpoint_testing.yaml']

    def test_anonymous_user_permissions(self) -> None:
        """Test unauthenticated users are returned a 401 status code for all request types"""

        endpoint = self.endpoint.format(pk=1)
        self.assertEqual(self.client.get(endpoint).status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(self.client.head(endpoint).status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(self.client.post(endpoint).status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(self.client.put(endpoint).status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(self.client.patch(endpoint).status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(self.client.delete(endpoint).status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(self.client.options(endpoint).status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(self.client.trace(endpoint).status_code, status.HTTP_401_UNAUTHORIZED)

    def test_authenticated_user_permissions(self) -> None:
        """Test general authenticated users have read-only permissions"""

        endpoint = self.endpoint.format(pk=1)
        user = User.objects.get(username='common_user')
        self.client.force_authenticate(user=user)

        # Allowed operations
        self.assertEqual(self.client.get(endpoint).status_code, status.HTTP_200_OK)
        self.assertEqual(self.client.head(endpoint).status_code, status.HTTP_200_OK)
        self.assertEqual(self.client.options(endpoint).status_code, status.HTTP_200_OK)

        # Unauthorized operations
        self.assertEqual(self.client.put(endpoint).status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(self.client.patch(endpoint).status_code, status.HTTP_403_FORBIDDEN)

        # Disallowed operations
        self.assertEqual(self.client.post(endpoint).status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
        self.assertEqual(self.client.trace(endpoint).status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_staff_user_permissions(self) -> None:
        """Test staff users have read and write permissions"""

        endpoint = self.endpoint.format(pk=1)
        user = User.objects.get(username='staff_user')
        self.client.force_authenticate(user=user)

        # Allowed operations
        self.assertEqual(self.client.get(endpoint).status_code, status.HTTP_200_OK)
        self.assertEqual(self.client.head(endpoint).status_code, status.HTTP_200_OK)
        self.assertEqual(self.client.options(endpoint).status_code, status.HTTP_200_OK)

        put = self.client.put(endpoint, data={'pk': 1, 'name': 'foo'})
        self.assertEqual(put.status_code, status.HTTP_200_OK)

        patch = self.client.patch(endpoint, data={'pk': 1, 'name': 'foo'})
        self.assertEqual(patch.status_code, status.HTTP_200_OK)

        # Disallowed operations
        self.assertEqual(self.client.post(endpoint).status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
        self.assertEqual(self.client.trace(endpoint).status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
