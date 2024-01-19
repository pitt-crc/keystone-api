"""General testing utilities."""

from django.test import Client


class CustomAsserts:
    """Custom assert methods for testing responses from REST endpoints"""

    client: Client
    assertEqual: callable

    def assert_http_responses(self, endpoint: str, **kwargs) -> None:
        """Execute a series of API calls and assert the returned status matches the given values

        Args:
            endpoint: The URL to perform requests against
            **<request>: The integer status cde expected by  given request type (get, post, etc.)
            **<request>_body: The data t include in the request (get_body, post_body, etc.)
        """

        http_methods = ['get', 'head', 'options', 'post', 'put', 'patch', 'delete', 'trace']
        for method in http_methods:
            expected_status = kwargs.get(method, None)
            if expected_status is not None:
                client_method = getattr(self.client, method)
                request_body = kwargs.get(f'{method}_body', None)
                request = client_method(endpoint, data=request_body)
                self.assertEqual(
                    expected_status, request.status_code,
                    f'{method} request received {request.status_code} instead of {expected_status}')
