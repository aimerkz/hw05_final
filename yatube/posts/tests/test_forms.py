import shutil
import tempfile


from django.conf import settings
from posts.forms import PostForm, CommentForm
from posts.models import Post, Group, Comment
from django.core.files.uploadedfile import SimpleUploadedFile
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import Client, TestCase, override_settings

User = get_user_model()


TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='TestArt')
        cls.group = Group.objects.create(
            title='Название группы для теста',
            slug='test-slug',
            description='Описание группы для теста'
        )
        cls.post = Post.objects.create(
            text='Текст поста для теста',
            author=cls.user,
            group=cls.group,
        )
        cls.form = PostForm()

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_create_post(self):
        """Валидная форма создает запись в Post."""
        # Посчитали количество постов
        posts_count = Post.objects.count()
        # Байт-последовательность картинки
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
        form_data = {
            'text': 'Текст поста для теста',
            'image': uploaded,
        }
        # Отправили POST-запрос
        response = self.authorized_client.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True
        )
        # Проверили редирект
        self.assertRedirects(response, reverse(
            'posts:profile', kwargs={'username': 'TestArt'})
        )
        # Снова проверили количество постов
        self.assertEqual(Post.objects.count(), posts_count + 1)
        # Проверили, что пост сохранился в бд
        self.assertTrue(
            Post.objects.filter(
                text='Текст поста для теста',
                image='posts/small.gif'
            ).exists()
        )

    def test_post_edit(self):
        """Валидная форма редактирует запись в Post."""
        form_data = {
            'text': 'Текст поста для теста_2',
            'group': self.group.pk,
        }
        # Отправили POST-запрос
        response = self.authorized_client.post(
            reverse('posts:post_edit', kwargs={'post_id': self.post.pk}),
            data=form_data
        )
        # Проверили редирект
        self.assertRedirects(response, reverse(
            'posts:post_detail', kwargs={'post_id': self.post.pk})
        )
        # Проверили, что пост обновлен
        self.assertTrue(
            Post.objects.filter(
                text='Текст поста для теста_2',
                group=self.group.pk
            ).exists())


class CommentFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='ArtComms')
        cls.group = Group.objects.create(
            title='Название группы для теста3',
            slug='test-slug3',
            description='Описание группы для теста3'
        )
        cls.post = Post.objects.create(
            text='Текст поста для теста3',
            author=cls.user,
            group=cls.group
        )
        cls.comment = Comment.objects.create(
            post=cls.post,
            author=cls.user,
            text='Текст коммента для теста'
        )
        cls.form = CommentForm()

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_add_comment(self):
        """Валидная форма создает комментарий."""
        form_data = {
            'post': self.post,
            'post_id': self.post.pk,
            'text': 'Текст коммента для теста',
        }
        # Отправили POST запрос
        response = self.authorized_client.post(
            reverse('posts:add_comment', kwargs={'post_id': self.post.pk}),
            data=form_data,
            follow=True
        )
        # Проверили редирект
        self.assertRedirects(response, reverse(
            'posts:post_detail', kwargs={'post_id': self.post.pk})
        )
        # Проверили, что коммент создан
        self.assertTrue(
            Comment.objects.filter(
                post=self.post,
                post_id=self.post.pk,
                text='Текст коммента для теста',
            ).exists()
        )

    def test_cant_add_comment(self):
        """Неавторизованный юзер не может добавить коммент."""
        # Посчитаем количество комментов
        comment_count = Comment.objects.count()
        form_data = {
            'post': self.post,
            'post_id': self.post.pk,
            'text': 'Текст коммента для теста',
        }
        # Отправили POST запрос
        response = self.guest_client.post(
            reverse('posts:add_comment', kwargs={'post_id': self.post.pk}),
            data=form_data,
            follow=True
        )
        # Проверим, что коммент не создан
        self.assertEqual(Comment.objects.all().count(), comment_count)
        # Проверили, что ничего не падает
        self.assertEqual(response.status_code, 200)
