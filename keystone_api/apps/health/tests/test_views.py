from unittest.mock import MagicMock

from django.http import JsonResponse
from django.test import TestCase

from apps.health.views import HealthChecks


class TestHealthChecks(TestCase):

    def create_mock_plugin(self, identifier, status, pretty_status, time_taken, critical_service) -> MagicMock:
        mock_plugin = MagicMock()
        mock_plugin.identifier.return_value = identifier
        mock_plugin.status = status
        mock_plugin.pretty_status.return_value = pretty_status
        mock_plugin.time_taken = time_taken
        mock_plugin.critical_service = critical_service
        return mock_plugin

    def test_render_response_to_json_500(self) -> None:
        expected_data = {
            'plugin1': {'status': 200, 'message': 'OK', 'time': 1.0, 'critical_service': True},
            'plugin2': {'status': 500, 'message': 'Error', 'time': 2.0, 'critical_service': False}
        }

        health_checks = [
            self.create_mock_plugin(**expected_data['plugin1']),
            self.create_mock_plugin(**expected_data['plugin2'])
        ]

        response = HealthChecks.render_to_response_json(health_checks, 500)
        self.assertIsInstance(response, JsonResponse)
        self.assertEqual(response.status_code, 500)
        self.assertEqual(response.json(), expected_data)
