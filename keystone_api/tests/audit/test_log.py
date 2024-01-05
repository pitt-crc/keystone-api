"""Tests for the `log` endpoint"""

from rest_framework import status
from rest_framework.test import APITestCase

from apps.users.models import User


class EndpointPermissions(APITestCase):
    """Test user permissions for the `/audit/log/` endpoint

    Endpoint permissions are tested against the following matrix of HTTP responses.

    | Authentication      | GET | HEAD | OPTIONS | POST | PUT | PATCH | DELETE | TRACE |
    |---------------------|-----|------|---------|------|-----|-------|--------|-------|
    | Anonymous User      | 401 | 401  | 401     | 401  | 401 | 401   | 401    | 401   |
    | Authenticated User  | 403 | 403  | 403     | 403  | 403 | 403   | 403    | 403   |
    | Staff User          | 200 | 200  | 200     | 405  | 405 | 405   | 405    | 405   |
    """

    endpoint = '/audit/log/'
    fixtures = ['multi_research_group.yaml']

    def test_anonymous_user_permissions(self) -> None:
        """Test annymous users are returned a 401 status code for all request types"""

        self.assertEqual(self.client.get(self.endpoint).status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(self.client.head(self.endpoint).status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(self.client.options(self.endpoint).status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(self.client.post(self.endpoint).status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(self.client.put(self.endpoint).status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(self.client.patch(self.endpoint).status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(self.client.delete(self.endpoint).status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(self.client.trace(self.endpoint).status_code, status.HTTP_401_UNAUTHORIZED)

    def test_authenticated_user_permissions(self) -> None:
        """Test general authenticated users are returned a 403 status code for all request types"""

        user = User.objects.get(username='common_user')
        self.client.force_authenticate(user=user)

        self.assertEqual(self.client.get(self.endpoint).status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(self.client.head(self.endpoint).status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(self.client.options(self.endpoint).status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(self.client.post(self.endpoint).status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(self.client.put(self.endpoint).status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(self.client.patch(self.endpoint).status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(self.client.delete(self.endpoint).status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(self.client.trace(self.endpoint).status_code, status.HTTP_403_FORBIDDEN)

    def test_staff_user_permissions(self) -> None:
        """Test staff users have read-only permissions"""

        user = User.objects.get(username='staff_user')
        self.client.force_authenticate(user=user)

        self.assertEqual(self.client.get(self.endpoint).status_code, status.HTTP_200_OK)
        self.assertEqual(self.client.head(self.endpoint).status_code, status.HTTP_200_OK)
        self.assertEqual(self.client.options(self.endpoint).status_code, status.HTTP_200_OK)

        self.assertEqual(self.client.post(self.endpoint).status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
        self.assertEqual(self.client.put(self.endpoint).status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
        self.assertEqual(self.client.patch(self.endpoint).status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
        self.assertEqual(self.client.delete(self.endpoint).status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
        self.assertEqual(self.client.trace(self.endpoint).status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
