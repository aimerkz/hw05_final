from django.urls import reverse
from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from posts.models import Post, Group
from django.core.cache import cache

User = get_user_model()


class PostIndexCacheTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='Art')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='Тестовый слаг',
            description='Тестовое описание'
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый текст для поста'
        )

    def setUp(self):
        self.guest_client = Client()

    def test_index_cache(self):
        """Проверка работы кэша на странице index."""
        # Посчитали количество постов
        posts_count_before = Post.objects.all().count()
        # Сделали запрос
        response_post_before = self.guest_client.get(reverse('posts:index'))
        # Результат запроса сохранили в переменную
        content_post_before = response_post_before.content
        # Удалили пост
        Post.objects.filter(pk=self.post.pk).delete()
        # Снова сделали запрос
        response_post_after = self.guest_client.get(reverse('posts:index'))
        # Снова сохранили результат запроса в переменную
        content_post_after = response_post_after.content
        # Снова посчитали количество постов
        posts_count_after = Post.objects.all().count()
        # Сравнили, что количество постов до != количеству после
        self.assertNotEqual(posts_count_before, posts_count_after)
        # Сравнили, что пост отображается с тем же контентом - кэш работает
        self.assertEqual(content_post_before, content_post_after)

        # Почистили кэш
        cache.clear()
        # Сделали новый запрос
        response_post_now = self.guest_client.get(reverse('posts:index'))
        # Сохранили контент запроса в переменную
        content_post_now = response_post_now
        # Сравнили, что пост отображается с другим контентом - кэш был удален
        self.assertNotEqual(content_post_now, content_post_before)
