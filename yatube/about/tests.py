from django.test import TestCase, Client
from http import HTTPStatus

from django.urls.base import reverse


class StaticURLTests(TestCase):
    def setUp(self):
        self.guest_client = Client()

    def test_about_urls_status(self):
        """Страницы author и tech доступны любому пользователю."""
        url_names = {
            reverse('about:author'): HTTPStatus.OK,
            reverse('about:tech'): HTTPStatus.OK,
        }
        for url, status_code in url_names.items():
            with self.subTest(url=url):
                response = self.guest_client.get(url)
                self.assertEqual(response.status_code, status_code)

    # Проверяем используемые шаблоны
    def test_pages_about_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        templates_pages_names = {
            'about/author.html': reverse('about:author'),
            'about/tech.html': reverse('about:tech'),
        }
        for template, reverse_name in templates_pages_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.guest_client.get(reverse_name)
                self.assertTemplateUsed(response, template)
