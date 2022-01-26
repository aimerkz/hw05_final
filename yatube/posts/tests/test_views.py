import shutil
import tempfile

from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile
from django.contrib.auth import get_user_model
from django.test import Client, TestCase, override_settings
from django.urls import reverse
from django import forms

from ..models import Post, Group, Comment, Follow

TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)
User = get_user_model()


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostPagesTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # Создали юзера
        cls.user = User.objects.create_user(
            username='TestArt'
        )
        # Создали группу
        cls.group = Group.objects.create(
            title='Название группы для теста',
            slug='test-slug',
            description='Описание группы для теста'
        )
        # Загрузили картинку
        small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        uploaded = SimpleUploadedFile(
            name='small.gif',
            content=small_gif,
            content_type='image/gif'
        )
        # Создали пост
        cls.post = Post.objects.create(
            author=cls.user,
            text='Текст поста для теста',
            group=cls.group,
            image=uploaded
        )
        # Создали коммент
        cls.comment = Comment.objects.create(
            post=cls.post,
            author=cls.user,
            text='Текст коммента для теста'
        )

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    # Проверяем используемые шаблоны
    def test_pages_posts_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        templates_pages_names = {
            'posts/index.html': reverse('posts:index'),
            'posts/group_list.html': (
                reverse('posts:group_list', kwargs={'slug': self.group.slug})
            ),
            'posts/profile.html': (
                reverse('posts:profile', kwargs={
                    'username': self.user.username})
            ),
            'posts/post_detail.html': (
                reverse('posts:post_detail', kwargs={'post_id': self.post.pk})
            ),
            'posts/create_post.html': reverse('posts:post_create'),
        }
        for template, reverse_name in templates_pages_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_page_post_edit_correct_tamplate(self):
        """URL-адрес использует соответствующий шаблон."""
        response = self.authorized_client.get(
            reverse('posts:post_edit', kwargs={'post_id': self.post.pk})
        )
        self.assertTemplateUsed(response, 'posts/create_post.html')

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    # Проверяем контекст
    def test_index_page_show_correct_context(self):
        """Шаблон index сформирован с правильным контекстом."""
        response = self.guest_client.get(reverse('posts:index'))
        first_object = response.context['page_obj'][0]
        post_text_0 = first_object.text
        post_group_0 = first_object.group
        post_image_0 = first_object.image
        self.assertEqual(post_text_0, 'Текст поста для теста')
        self.assertEqual(post_group_0, self.group)
        self.assertEqual(post_image_0, Post.objects.first().image)

    def test_group_list_page_show_correct_context(self):
        """Шаблон group_list сформирован с правильным контекстом."""
        response = self.guest_client.get(
            reverse('posts:group_list', kwargs={'slug': self.group.slug})
        )
        first_object = response.context['page_obj'][0]
        post_text_0 = first_object.text
        post_group_0 = first_object.group
        post_image_0 = first_object.image
        self.assertEqual(post_text_0, 'Текст поста для теста')
        self.assertEqual(post_group_0, self.group)
        self.assertEqual(post_image_0, Post.objects.first().image)

    def test_profile_page_show_correct_context(self):
        """Шаблон profile сформирован с правильным контекстом."""
        response = self.authorized_client.get(
            reverse('posts:profile', kwargs={'username': self.user.username})
        )
        first_object = response.context['page_obj'][0]
        post_text_0 = first_object.text
        post_author_0 = first_object.author
        post_image_0 = first_object.image
        self.assertEqual(post_text_0, 'Текст поста для теста')
        self.assertEqual(post_author_0, self.user)
        self.assertEqual(post_image_0, Post.objects.first().image)

    def test_post_detail_page_show_correct_context(self):
        """Шаблон post_detail сформирован с правильным контекстом."""
        response = self.authorized_client.get(
            reverse('posts:post_detail', kwargs={'post_id': self.post.pk}))
        self.assertEqual(
            response.context['posts'].text, 'Текст поста для теста'
        )
        self.assertEqual(
            response.context['posts'].image, Post.objects.get(pk=1).image
        )
        self.assertEqual(
            response.context['comments'][0].text, 'Текст коммента для теста'
        )

    def test_post_detail_comment_context(self):
        """Шаблон post_detail сформирован с правильным контекстом."""
        form_field = {'text': forms.fields.CharField}

        response = self.authorized_client.get(
            reverse(
                'posts:post_detail',
                kwargs={'post_id': Post.objects.first().pk},
            )
        )

        comment_form = response.context['form'].fields['text']
        self.assertIsInstance(comment_form, form_field['text'])

    def test_post_create_page_show_correct_context(self):
        """Шаблон create_post сформирован с правильным контекстом."""
        response = self.authorized_client.get(reverse('posts:post_create'))
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)

    def test_post_create_page_show_correct_context(self):
        """Шаблон create_post (для редактирования поста)
        сформирован с правильным контекстом."""
        response = self.authorized_client.get(
            reverse('posts:post_edit', kwargs={'post_id': self.post.pk})
        )
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)


# Тестируем паджинатор
class PaginatorViewsTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # Создали юзера
        cls.user2 = User.objects.create_user(
            username='TestArt2'
        )
        # Создали группу
        cls.group2 = Group.objects.create(
            title='Название группы для теста2',
            slug='test-slug2',
            description='Описание группы для теста2'
        )
        # Пустой список постов
        cls.post_list = []
        # Создали 13 постов, добавили в список
        for i in range(1, 14):
            cls.post_list.append(Post(
                author=cls.user2,
                text=f'Текст поста для теста {i}',
                group=cls.group2
            ))
        # Сохранили в бд
        cls.post_list = Post.objects.bulk_create(cls.post_list)

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user2)

    def test_pages_paginator(self):
        """Paginator in tested templates correct."""
        reverses_names = [
            reverse('posts:index'),
            reverse('posts:group_list', kwargs={'slug': self.group2.slug}),
            reverse('posts:profile', kwargs={'username': self.user2.username})
        ]
        for reverses_item in reverses_names:
            with self.subTest(reverses_item=reverses_item):
                response = self.authorized_client.get(reverses_item)
                self.assertEqual(len(response.context['page_obj']), 10)

        for reverses_item in reverses_names:
            with self.subTest(reverses_item=reverses_item):
                response = self.authorized_client.get(
                    reverses_item + '?page=2')
                self.assertEqual(len(response.context['page_obj']), 3)


# Тестируем подписки
class FollowTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # Создали юзера-подписчика
        cls.user_follower = User.objects.create_user(
            username='TestArtttt'
        )
        # Создали юзера-автора
        cls.user_author = User.objects.create_user(
            username='TestAuthor'
        )
        # Создали группу
        cls.group = Group.objects.create(
            title='Название группы для теста подписки',
            slug='test-slug_follow',
            description='Описание группы для теста подписок'
        )
        # Создали пост
        cls.post = Post.objects.create(
            author=cls.user_author,
            text='Текст поста для теста подписки',
            group=cls.group
        )

    def setUp(self):
        self.client_user = Client()
        self.client_user.force_login(self.user_follower)
        self.client_author = Client()
        self.client_author.force_login(self.user_author)

    def test_follow(self):
        """Авторизованный пользователь может подписываться на
        других пользователей."""
        # Посчитали количество подписок
        count_follow = Follow.objects.count()
        # Пост-запрос
        response = self.client_user.post(reverse(
            'posts:profile_follow', kwargs={
                'username': self.user_author.username}
        ))
        # Проверили редирект
        self.assertRedirects(response, reverse(
            'posts:profile', kwargs={'username': self.user_author.username}
        ))
        # Снова посчитали количество подписок
        self.assertEqual(Follow.objects.count(), count_follow + 1)
        # Проверили, что подписка активна
        self.assertTrue(self.user_follower, self.user_author)

    def test_unfollow(self):
        """Авторизованный пользователь может отписаться
        от других пользователей."""
        # Оформили подписку
        follow = Follow.objects.create(
            author=self.user_author, user=self.user_follower)
        # Посчитали количество подписок
        count_follow = Follow.objects.count()
        # Пост-запрос на отписку
        response = self.client_user.post(reverse(
            'posts:profile_unfollow', kwargs={
                'username': self.user_author.username}
        ))
        # Проверили редирект
        self.assertRedirects(response, reverse(
            'posts:profile', kwargs={'username': self.user_author.username}
        ))
        # Снова посчитали количество подписок
        self.assertEqual(
            Follow.objects.count(), count_follow - 1)
        # Проверили, что подписки нет
        self.assertNotIn(follow, Follow.objects.all())

    def test_follow_authors(self):
        """Новая запись автора появляется только
        в ленте подписчика."""
        # Оформили подписку
        Follow.objects.create(
            author=self.user_author, user=self.user_follower)
        # Взяли какой-то пост
        post = self.post
        # Сделали get-запрос
        response = self.client_user.get(reverse(
            'posts:follow_index'))
        # Проверили, что отобразились посты автора, на которого подписаны
        self.assertIn(post, response.context['page_obj'])

    def test_unfollow_authors(self):
        """Новая запись автора не появляется в ленте
        неподписанного юзера."""
        # Взяли пост
        post = self.post
        # Сделали get-запрос
        response = self.client_user.get(reverse(
            'posts:follow_index'))
        # Проверили, что отобразились посты автора, на которого подписаны
        self.assertNotIn(post, response.context['page_obj'])
