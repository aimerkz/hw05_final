from django.test import TestCase, Client
from http import HTTPStatus
from django.urls import reverse
from django import forms
from django.contrib.auth import get_user_model

User = get_user_model()


class StaticURLTests(TestCase):

    def setUp(self):
        self.guest_client = Client()
        self.user = User.objects.create_user(username='TestArtem')
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_users_urls_status(self):
        """Страницы регистрации, входа и сброса пароля
        доступны любому пользователю."""
        url_names = {
            reverse('users:signup'): HTTPStatus.OK,
            reverse('users:login'): HTTPStatus.OK,
            reverse('users:password_reset_form'): HTTPStatus.OK,
            reverse('users:password_reset_done'): HTTPStatus.OK,
        }
        for url, status_code in url_names.items():
            with self.subTest(url=url):
                response = self.guest_client.get(url)
                self.assertEqual(response.status_code, status_code)

    def test_users_urls_auth_status(self):
        """Страницы изменения пароля и выхода
        доступны только авторизованному пользователю."""
        url_names = {
            reverse('users:password_change_form'): HTTPStatus.OK,
            reverse('users:logout'): HTTPStatus.OK,
        }
        for url, status_code in url_names.items():
            with self.subTest(url=url):
                response = self.authorized_client.get(url)
                self.assertEqual(response.status_code, status_code)

    # Проверяем используемые шаблоны
    def test_pages_users_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        templates_pages_names = {
            'users/login.html': reverse('users:login'),
            'users/signup.html': reverse('users:signup'),
            'users/password_change_form.html': reverse(
                'users:password_change_form'
            ),
            'users/password_reset_form.html': reverse(
                'users:password_reset_form'
            ),
            'users/logged_out.html': reverse('users:logout'),
        }
        for template, reverse_name in templates_pages_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    # Проверяем контекст
    def test_signup_page_show_correct_context(self):
        """Шаблон signup сформирован с правильным контекстом."""
        response = self.authorized_client.get(reverse('users:signup'))
        form_fields = {
            'first_name': forms.fields.CharField,
            'last_name': forms.fields.CharField,
            'username': forms.fields.CharField,
            'email': forms.fields.EmailField,
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)


# Проверяем форму создания юзера
class CreationFormTests(TestCase):

    def setUp(self):
        self.guest_client = Client()

    def test_signup(self):
        """Валидная форма создает юзера."""
        form_data = {
            'username': 'TestArt',
            'first_name': 'Test',
            'last_name': 'Testovich',
            'email': 'testovich@yandex.ru',
            'password1': 'Parol123',
            'password2': 'Parol123',
        }
        # Отправили POST-запрос
        response = self.guest_client.post(
            reverse('users:signup'),
            data=form_data,
            follow=True
        )
        # Проверили редирект
        self.assertRedirects(response, reverse('posts:index'))
        # Проверили, что создали нового юзера
        self.assertTrue(
            User.objects.filter(
                username='TestArt',
                first_name='Test',
                last_name='Testovich',
                email='testovich@yandex.ru'
            ).exists())
