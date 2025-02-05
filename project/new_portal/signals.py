from django.db.models.signals import m2m_changed
from django.dispatch import receiver

from .models import PostCategory
from .tasks import with_every_new_post


@receiver(m2m_changed, sender=PostCategory)                    # instance будет по модели Post
def post_created(sender, instance, action, **kwargs):
    if action == 'post_add':                                   # Проверяем, что действие - добавление поста
        with_every_new_post.delay(instance.pk)                 # вызываем нашу таску и передаем ей необходимые аргументы

