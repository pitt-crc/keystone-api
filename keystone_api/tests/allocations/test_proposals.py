"""Tests for the `proposals` endpoint"""

from rest_framework import status
from rest_framework.test import APITestCase

from apps.users.models import User


class ListEndpointPermissions(APITestCase):
    """Test user permissions for the `/allocations/proposals/` endpoint

    Endpoint permissions are tested against the following matrix of HTTP responses.
    All listed responses assume the associated HTTP request is otherwise valid.

    | Authentication | GET | HEAD | OPTIONS | POST | PUT | PATCH | DELETE | TRACE |
    |----------------|-----|------|---------|------|-----|-------|--------|-------|
    | Anonymous User | 401 | 401  | 401     | 401  | 401 | 401   | 401    | 401   |
    | Non-Member     | 200 | 200  | 200     | 403  | 403 | 403   | 403    | 403   |
    | Group Member   | 200 | 200  | 200     | 403  | 403 | 403   | 403    | 403   |
    | Group Admin    | 200 | 200  | 200     | 201  | 403 | 403   | 403    | 403   |
    | Group PI       | 200 | 200  | 200     | 201  | 403 | 403   | 403    | 403   |
    | Staff User     | 200 | 200  | 200     | 201  | 405 | 405   | 405    | 405   |
    """

    endpoint = '/allocations/proposals/'
    fixtures = ['multi_research_group.yaml']

    def test_anonymous_user_permissions(self) -> None:
        """Test unauthenticated users cannot access resources"""

        self.assertEqual(self.client.get(self.endpoint).status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(self.client.head(self.endpoint).status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(self.client.options(self.endpoint).status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(self.client.post(self.endpoint).status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(self.client.put(self.endpoint).status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(self.client.patch(self.endpoint).status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(self.client.delete(self.endpoint).status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(self.client.trace(self.endpoint).status_code, status.HTTP_401_UNAUTHORIZED)

    def test_non_group_member_permissions(self) -> None:
        """Test authenticated users have read access but cannot create records for research groups they are not a part of"""

        # Record data reflects a group ID for which the user is not a member
        self.client.force_authenticate(user=User.objects.get(username='generic_user'))
        record_data = {'title': 'foo', 'description': 'bar', 'group': 1}

        # Allowed operations
        self.assertEqual(self.client.get(self.endpoint).status_code, status.HTTP_200_OK)
        self.assertEqual(self.client.head(self.endpoint).status_code, status.HTTP_200_OK)
        self.assertEqual(self.client.options(self.endpoint).status_code, status.HTTP_200_OK)

        # Forbidden operations
        self.assertEqual(self.client.post(self.endpoint, data=record_data).status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(self.client.put(self.endpoint, data=record_data).status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(self.client.patch(self.endpoint, data=record_data).status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(self.client.delete(self.endpoint).status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(self.client.trace(self.endpoint).status_code, status.HTTP_403_FORBIDDEN)

    def test_group_member_permissions(self) -> None:
        """Test regular research group members have read-only access"""

        # Record data reflects a group ID for which the user is a regular member
        self.client.force_authenticate(user=User.objects.get(username='member_1'))
        record_data = {'title': 'foo', 'description': 'bar', 'group': 1}

        # Allowed operations
        self.assertEqual(self.client.get(self.endpoint).status_code, status.HTTP_200_OK)
        self.assertEqual(self.client.head(self.endpoint).status_code, status.HTTP_200_OK)
        self.assertEqual(self.client.options(self.endpoint).status_code, status.HTTP_200_OK)

        # Forbidden operations
        self.assertEqual(self.client.post(self.endpoint, data=record_data).status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(self.client.put(self.endpoint, data=record_data).status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(self.client.patch(self.endpoint, data=record_data).status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(self.client.delete(self.endpoint).status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(self.client.trace(self.endpoint).status_code, status.HTTP_403_FORBIDDEN)

    def test_group_admin_permissions(self) -> None:
        """Test research group admins have read and write access"""

        # Record data reflects a group ID for which the user is an admin
        self.client.force_authenticate(user=User.objects.get(username='group_admin_1'))
        record_data = {'title': 'foo', 'description': 'bar', 'group': 1}

        # Allowed operations
        self.assertEqual(self.client.get(self.endpoint).status_code, status.HTTP_200_OK)
        self.assertEqual(self.client.head(self.endpoint).status_code, status.HTTP_200_OK)
        self.assertEqual(self.client.options(self.endpoint).status_code, status.HTTP_200_OK)
        self.assertEqual(self.client.post(self.endpoint, record_data).status_code, status.HTTP_201_CREATED)

        # Forbidden operations
        self.assertEqual(self.client.put(self.endpoint).status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(self.client.patch(self.endpoint).status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(self.client.delete(self.endpoint).status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(self.client.trace(self.endpoint).status_code, status.HTTP_403_FORBIDDEN)

    def test_group_pi_permissions(self) -> None:
        """Test research group PIs have read and write access"""

        # Record data reflects a group ID for which the user is a PI
        self.client.force_authenticate(user=User.objects.get(username='pi_1'))
        record_data = {'title': 'foo', 'description': 'bar', 'group': 1}

        # Allowed operations
        self.assertEqual(self.client.get(self.endpoint).status_code, status.HTTP_200_OK)
        self.assertEqual(self.client.head(self.endpoint).status_code, status.HTTP_200_OK)
        self.assertEqual(self.client.options(self.endpoint).status_code, status.HTTP_200_OK)
        self.assertEqual(self.client.post(self.endpoint, record_data).status_code, status.HTTP_201_CREATED)

        # Forbidden operations
        self.assertEqual(self.client.put(self.endpoint).status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(self.client.patch(self.endpoint).status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(self.client.delete(self.endpoint).status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(self.client.trace(self.endpoint).status_code, status.HTTP_403_FORBIDDEN)

    def test_staff_user(self) -> None:
        """Test staff users have read and write permissions"""

        user = User.objects.get(username='staff_user')
        self.client.force_authenticate(user=user)

        # Allowed operations
        self.assertEqual(self.client.get(self.endpoint).status_code, status.HTTP_200_OK)
        self.assertEqual(self.client.head(self.endpoint).status_code, status.HTTP_200_OK)
        self.assertEqual(self.client.options(self.endpoint).status_code, status.HTTP_200_OK)

        post = self.client.post(self.endpoint, {'title': 'foo', 'description': 'bar', 'group': 1})
        self.assertEqual(post.status_code, status.HTTP_201_CREATED)

        # Disallowed operations
        self.assertEqual(self.client.put(self.endpoint).status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
        self.assertEqual(self.client.patch(self.endpoint).status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
        self.assertEqual(self.client.delete(self.endpoint).status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
        self.assertEqual(self.client.trace(self.endpoint).status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
