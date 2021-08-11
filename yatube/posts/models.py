from django.contrib.auth import get_user_model
from django.db import models

from .validators import validate_not_empty

User = get_user_model()


class Group(models.Model):
    """Модель групп пользователей."""
    title = models.CharField('Заголовок группы', max_length=200)
    slug = models.SlugField('Адрес группы', unique=True)
    description = models.TextField('Описание группы')

    def __str__(self) -> str:
        return self.title


class Post(models.Model):
    """Модель постов пользователей."""
    text = models.TextField('Текст', validators=[validate_not_empty])
    pub_date = models.DateTimeField(
        'Дата поста',
        auto_now_add=True,
        db_index=True
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='posts'
    )
    group = models.ForeignKey(
        Group,
        verbose_name='Группа',
        on_delete=models.SET_NULL,
        related_name='posts',
        blank=True,
        null=True
    )
    image = models.ImageField(
        'Изображение',
        upload_to='posts/',
        blank=True, null=True
    )

    def __str__(self):
        return self.text[:15]

    class Meta:
        ordering = ('-pub_date',)
        verbose_name = 'Пост'
        verbose_name_plural = 'Посты'


class Comment(models.Model):
    """Модель комментаривания пользователей."""
    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        related_name='comments',
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name='Автор комментария',
    )
    text = models.TextField(verbose_name='Текст')
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.text


class Follow(models.Model):
    """Модель подписки на авторов."""
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='follower',
        verbose_name='Подписчик'
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='following',
        verbose_name='Избранный автор'
    )

    class Meta:
        unique_together = ['user', 'author']
