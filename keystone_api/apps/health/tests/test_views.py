from unittest.mock import Mock, patch

from django.core.handlers.wsgi import HttpRequest
from django.http import JsonResponse
from django.test import TestCase

from keystone_api.apps.health.views import HealthChecks


class HealthChecksTestCase(TestCase):

    def test_list_method_returns_json_response(self):
        request = HttpRequest()
        health_checks_view = HealthChecks()

        with patch.object(health_checks_view, 'render_to_response_json') as mock_render_json:
            response = health_checks_view.list(request)

        mock_render_json.assert_called_once_with(health_checks_view.plugins, 200)
        self.assertIsInstance(response, JsonResponse)
        self.assertEqual(response.status_code, 200)

    def test_render_to_response_json_method(self):
        health_checks_view = HealthChecks()
        plugins = [Mock(identifier=lambda: 'plugin1', status=True, pretty_status=lambda: 'OK', time_taken=1, critical_service=False)]

        response = health_checks_view.render_to_response_json(plugins, 200)
        data = response.json()

        self.assertEqual(response.status_code, 200)
        self.assertIn('plugin1', data)
        self.assertEqual(data['plugin1']['status'], 200)
        self.assertEqual(data['plugin1']['message'], 'OK')
        self.assertEqual(data['plugin1']['time'], 1)
        self.assertFalse(data['plugin1']['critical_service'])

    def test_list_method_with_errors(self):
        request = HttpRequest()
        health_checks_view = HealthChecks()
        health_checks_view.errors = True

        with patch.object(health_checks_view, 'render_to_response_json') as mock_render_json:
            response = health_checks_view.list(request)

        mock_render_json.assert_called_once_with(health_checks_view.plugins, 500)
        self.assertIsInstance(response, JsonResponse)
        self.assertEqual(response.status_code, 500)
