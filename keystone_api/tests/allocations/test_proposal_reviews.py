"""Tests for the `proposal-reviews` endpoint"""

from rest_framework import status
from rest_framework.test import APITestCase

from apps.users.models import User


class ListEndpointPermissions(APITestCase):
    """Test user permissions for the `/allocations/proposal-reviews/` endpoint

    Endpoint permissions are tested against the following matrix of HTTP responses.
    All listed responses assume the associated HTTP request is otherwise valid.

    | Authentication      | GET | HEAD | OPTIONS | POST | PUT | PATCH | DELETE | TRACE |
    |---------------------|-----|------|---------|------|-----|-------|--------|-------|
    | Anonymous User      | 401 | 401  | 401     | 401  | 401 | 401   | 401    | 401   |
    | Authenticated User  | 200 | 200  | 200     | 403  | 403 | 403   | 403    | 403   |
    | Staff User          | 200 | 200  | 200     | 201  | 405 | 405   | 405    | 405   |
    """

    endpoint = '/allocations/proposal-reviews/'
    fixtures = ['multi_research_group.yaml']

    def test_anonymous_user_permissions(self) -> None:
        """Test unauthenticated users are returned a 401 status code for all request types"""

        self.assertEqual(self.client.get(self.endpoint).status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(self.client.head(self.endpoint).status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(self.client.options(self.endpoint).status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(self.client.post(self.endpoint).status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(self.client.put(self.endpoint).status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(self.client.patch(self.endpoint).status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(self.client.delete(self.endpoint).status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(self.client.trace(self.endpoint).status_code, status.HTTP_401_UNAUTHORIZED)

    def test_authenticated_user_permissions(self) -> None:
        """Test general authenticated users have read-only permissions"""

        user = User.objects.get(username='generic_user')
        self.client.force_authenticate(user=user)

        # Allowed operations
        self.assertEqual(self.client.get(self.endpoint).status_code, status.HTTP_200_OK)
        self.assertEqual(self.client.head(self.endpoint).status_code, status.HTTP_200_OK)
        self.assertEqual(self.client.options(self.endpoint).status_code, status.HTTP_200_OK)

        # Forbidden operations
        self.assertEqual(self.client.post(self.endpoint).status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(self.client.put(self.endpoint).status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(self.client.patch(self.endpoint).status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(self.client.delete(self.endpoint).status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(self.client.trace(self.endpoint).status_code, status.HTTP_403_FORBIDDEN)

    def test_staff_user_permissions(self) -> None:
        """Test staff users have read and write permissions"""

        user = User.objects.get(username='staff_user')
        self.client.force_authenticate(user=user)

        # Allowed operations
        self.assertEqual(self.client.get(self.endpoint).status_code, status.HTTP_200_OK)
        self.assertEqual(self.client.head(self.endpoint).status_code, status.HTTP_200_OK)
        self.assertEqual(self.client.options(self.endpoint).status_code, status.HTTP_200_OK)

        post = self.client.post(self.endpoint, data={'approve': True, 'proposal': 1})
        self.assertEqual(post.status_code, status.HTTP_201_CREATED)

        # Disallowed operations
        self.assertEqual(self.client.put(self.endpoint).status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
        self.assertEqual(self.client.patch(self.endpoint).status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
        self.assertEqual(self.client.delete(self.endpoint).status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
        self.assertEqual(self.client.trace(self.endpoint).status_code, status.HTTP_405_METHOD_NOT_ALLOWED)



class RecordEndpointPermissions(APITestCase):
    """Test user permissions against the `/allocations/allocations/<pk>` endpoint

    Permissions depend on whether the user is a member of the record's associated research group.

    Endpoint permissions are tested against the following matrix of HTTP responses.
    All listed responses assume the associated HTTP request is otherwise valid.

    | Authentication              | GET | HEAD | OPTIONS | POST | PUT | PATCH | DELETE | TRACE |
    |-----------------------------|-----|------|---------|------|-----|-------|--------|-------|
    | Anonymous User              | 401 | 401  | 401     | 401  | 401 | 401   | 401    | 401   |
    | User accessing own group    | 200 | 200  | 200     | 403  | 403 | 403   | 403    | 403   |
    | User accessing other group  | 404 | 404  | 200     | 403  | 403 | 403   | 403    | 403   |
    | Staff User                  | 200 | 200  | 200     | 405  | 200 | 200   | 204    | 405   |
    """

    endpoint = '/allocations/proposal-reviews/{pk}/'
    fixtures = ['multi_research_group.yaml']

    def test_anonymous_user_permissions(self) -> None:
        """Test unauthenticated users cannot access resources"""

        endpoint = self.endpoint.format(pk=1)
        self.assertEqual(self.client.get(endpoint).status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(self.client.head(endpoint).status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(self.client.options(endpoint).status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(self.client.post(endpoint).status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(self.client.put(endpoint).status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(self.client.patch(endpoint).status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(self.client.delete(endpoint).status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(self.client.trace(endpoint).status_code, status.HTTP_401_UNAUTHORIZED)

    def test_authenticated_user_same_group(self) -> None:
        """Test permissions for authenticated users accessing records owned by their research group"""

        # Define a user / record endpoint from the SAME research groups
        endpoint = self.endpoint.format(pk=1)
        user = User.objects.get(username='member_1')
        self.client.force_authenticate(user=user)

        self.assertEqual(self.client.get(endpoint).status_code, status.HTTP_200_OK)
        self.assertEqual(self.client.head(endpoint).status_code, status.HTTP_200_OK)
        self.assertEqual(self.client.options(endpoint).status_code, status.HTTP_200_OK)

        # Regular users do not have write permissions on this endpoint
        self.assertEqual(self.client.post(endpoint).status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(self.client.put(endpoint).status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(self.client.patch(endpoint).status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(self.client.delete(endpoint).status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(self.client.trace(endpoint).status_code, status.HTTP_403_FORBIDDEN)

    def test_authenticated_user_different_group(self) -> None:
        """Test permissions for authenticated users accessing records owned by someone else's research group"""

        # Define a user  / record endpoint from DIFFERENT research groups
        endpoint = self.endpoint.format(pk=1)
        user = User.objects.get(username='member_2')
        self.client.force_authenticate(user=user)

        self.assertEqual(self.client.get(endpoint).status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(self.client.head(endpoint).status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(self.client.options(endpoint).status_code, status.HTTP_200_OK)

        # Regular users d nt have write permissions on this endpoint
        self.assertEqual(self.client.post(endpoint).status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(self.client.put(endpoint).status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(self.client.patch(endpoint).status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(self.client.delete(endpoint).status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(self.client.trace(endpoint).status_code, status.HTTP_403_FORBIDDEN)

    def test_staff_user_permissions(self) -> None:
        """Test staff users have read and write permissions"""

        endpoint = self.endpoint.format(pk=1)
        user = User.objects.get(username='staff_user')
        self.client.force_authenticate(user=user)

        # Allowed operations
        self.assertEqual(self.client.get(endpoint).status_code, status.HTTP_200_OK)
        self.assertEqual(self.client.head(endpoint).status_code, status.HTTP_200_OK)
        self.assertEqual(self.client.options(endpoint).status_code, status.HTTP_200_OK)

        self.assertEqual(self.client.post(endpoint).status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

        put = self.client.put(endpoint, data={'approve': 1, 'proposal': 1})
        self.assertEqual(put.status_code, status.HTTP_200_OK)

        patch = self.client.patch(endpoint, data={'approve': True})
        self.assertEqual(patch.status_code, status.HTTP_200_OK)

        self.assertEqual(self.client.delete(endpoint).status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(self.client.trace(endpoint).status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
