from django.urls import reverse
from django.contrib.auth import get_user_model
from django.test import TestCase, Client
from http import HTTPStatus

from posts.models import Post, Group

User = get_user_model()


class PostURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='TestArt')
        cls.group = Group.objects.create(
            title='Название группы для теста',
            slug='test-slug',
            description='Описание группы для теста',
        )
        cls.post = Post.objects.create(
            text='Текст поста для теста',
            author=cls.user,
            group=cls.group,
        )

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_posts_page(self):
        """Страницы index, group_list, profile,
        post_detail доступны любому пользователю."""
        url_names = {
            reverse('posts:index'): HTTPStatus.OK,
            reverse('posts:group_list', kwargs={
                'slug': self.group.slug}): HTTPStatus.OK,
            reverse('posts:profile', kwargs={
                'username': self.user.username}): HTTPStatus.OK,
            reverse('posts:post_detail', kwargs={
                'post_id': self.post.pk}): HTTPStatus.OK,
        }
        for url, status_code in url_names.items():
            with self.subTest(url=url):
                response = self.guest_client.get(url)
                self.assertEqual(response.status_code, status_code)

    def test_unexisting_page(self):
        """Страница не существует."""
        response = self.guest_client.get('none')
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)

    def test_create_page(self):
        """Страница create доступна только авторизованному пользователю."""
        response = self.authorized_client.get(reverse('posts:post_create'))
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_post_edit_page(self):
        """Страница post_edit доступна только автору поста."""
        response = self.authorized_client.get(
            reverse('posts:post_edit', kwargs={'post_id': self.post.pk})
        )
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_urls_posts_template(self):
        """URL-адрес использует соответствующий шаблон."""
        templates_url_names = {
            reverse('posts:index'): 'posts/index.html',
            reverse('posts:group_list', kwargs={
                'slug': self.group.slug}): 'posts/group_list.html',
            reverse('posts:profile', kwargs={
                'username': self.user.username}): 'posts/profile.html',
            reverse('posts:post_detail', kwargs={
                'post_id': self.post.pk}): 'posts/post_detail.html',
            reverse('posts:post_edit', kwargs={
                'post_id': self.post.pk}): 'posts/create_post.html',
            reverse('posts:post_create'): 'posts/create_post.html',
        }
        for address, template in templates_url_names.items():
            with self.subTest(address=address):
                response = self.authorized_client.get(address)
                self.assertTemplateUsed(response, template)
