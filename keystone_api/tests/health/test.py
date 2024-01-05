"""Tests for the `health` endpoint"""

from rest_framework import status
from rest_framework.test import APITestCase


class EndpointPermissions(APITestCase):
    """Test user permissions for the `/health/` endpoint

    Endpoint permissions are tested against the following matrix of HTTP responses.

    | Authentication      | GET     | HEAD     | OPTIONS | POST | PUT | PATCH | DELETE | TRACE |
    |---------------------|---------|----------|---------|------|-----|-------|--------|-------|
    | Anonymous User      | 200/500 | 200/500  | 200/500 | 405  | 405 | 405   | 405    | 405   |
    """

    endpoint = '/health/'

    def test_anonymous_user_permissions(self) -> None:
        """Test unauthenticated users have read-only access"""

        valid_response_codes = (status.HTTP_200_OK, status.HTTP_500_INTERNAL_SERVER_ERROR)

        self.assertIn(self.client.get(self.endpoint).status_code, valid_response_codes)
        self.assertIn(self.client.head(self.endpoint).status_code, valid_response_codes)
        self.assertIn(self.client.options(self.endpoint).status_code, valid_response_codes)

        self.assertEqual(self.client.post(self.endpoint).status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
        self.assertEqual(self.client.put(self.endpoint).status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
        self.assertEqual(self.client.patch(self.endpoint).status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
        self.assertEqual(self.client.delete(self.endpoint).status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
        self.assertEqual(self.client.trace(self.endpoint).status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
