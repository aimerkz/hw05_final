from django.db import models
from core.models import CreatedModel
from django.contrib.auth import get_user_model

User = get_user_model()


class Group(models.Model):
    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=50, unique=True)
    description = models.TextField()

    class Meta:
        verbose_name = 'Группа'
        verbose_name_plural = 'Группы'

    def __str__(self) -> str:
        return self.title


class Post(CreatedModel):
    text = models.TextField(
        'Текст поста',
        help_text='Введите текст поста'
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='posts',
        verbose_name='Автор'
    )
    group = models.ForeignKey(
        Group,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name='posts',
        verbose_name='Группы',
        help_text='Выберите группу'
    )
    image = models.ImageField(
        'Картинка',
        upload_to='posts/',
        blank=True,
        null=True,
        help_text='Загрузите картинку'
    )

    class Meta:
        ordering = ['-pub_date']
        verbose_name = 'Пост'
        verbose_name_plural = 'Посты'

    def __str__(self) -> str:
        return self.text[:15]


class Comment(models.Model):
    text = models.TextField(
        'Текст комментария',
        help_text='Введите комментарий'
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name='Автор'
    )
    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name='Комментарий к посту'
    )
    created = models.DateTimeField(
        'Дата комментария',
        auto_now_add=True
    )

    class Meta:
        ordering = ['created']
        verbose_name = 'Комментарий'
        verbose_name_plural = 'Комментарии'

    def __str__(self) -> str:
        return f'{self.author} написал {self.text[:15]}'


class Follow(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='follower',
        verbose_name='Имя пользователя'
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='following',
        verbose_name='Автор поста',
    )

    class Meta:
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'

    def __str__(self) -> str:
        return f'{self.user} подписан на {self.author}'
