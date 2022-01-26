from django.test import TestCase, Client
from http import HTTPStatus


class CoreURLTests(TestCase):
    def setUp(self):
        self.guest_client = Client()

    def test_core_error_page(self):
        """Страница 404 отдает кастомный шаблон."""
        response = self.guest_client.get('/bla_bla')
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        self.assertTemplateUsed(response, 'core/404.html')
