
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.dispatch import receiver
from django.db import models
from django.db.models.signals import pre_save


from core.models import CreatedModel

User = get_user_model()


class Post(CreatedModel):
    text = models.TextField('Текст поста', help_text='Сообщение')
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='posts',
        verbose_name='автор',
    )
    group = models.ForeignKey(
        'Group',
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        related_name='groups',
        verbose_name='группа',
        help_text='Группа, которой пренадлежит пост',
    )
    image = models.ImageField(
        'Картинка',
        upload_to='posts/',
        blank=True,
    )

    class Meta:
        ordering = ('-created',)
        verbose_name = 'пост'
        verbose_name_plural = 'посты'

    def __str__(self) -> str:
        return self.text[:15]


class Group(models.Model):
    title = models.CharField('Называние группы', max_length=200)
    slug = models.SlugField('Ссылка группы', unique=True)
    description = models.TextField('Описание')

    class Meta:
        verbose_name = 'группу'
        verbose_name_plural = 'группы'

    def __str__(self) -> str:
        return self.title


class Comment(CreatedModel):
    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name='Пост',
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name='Автор',
    )
    text = models.TextField(
        'Текст комментария', help_text={
            'post': 'Пост, к которому сделан комментарий',
            'text': 'Текст комментария',
        }
    )

    class Meta:
        ordering = ('-created',)
        verbose_name = 'комментарий'
        verbose_name_plural = 'комментарии'


class Follow(models.Model):
    user = models.ForeignKey(
        User,
        related_name='follower',
        verbose_name='подписчик',
        on_delete=models.CASCADE,
        help_text='подписчик',
    )
    author = models.ForeignKey(
        User,
        related_name='following',
        verbose_name='подписка на',
        on_delete=models.CASCADE,
        help_text='подписка на',
    )

    class Meta:
        verbose_name = 'подписку'
        verbose_name_plural = 'подписки'
        unique_together = (
            ('user', 'author'),
        )


@receiver(pre_save, sender=Follow)
def check_self_following(sender, instance, **kwargs):
    if instance.author == instance.user:
        raise ValidationError('Нельзя подписываться на самого себя')
