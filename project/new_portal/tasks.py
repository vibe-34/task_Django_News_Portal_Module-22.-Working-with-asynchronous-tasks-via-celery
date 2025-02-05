from django.conf import settings
from django.contrib.auth.models import User
from django.core.mail import EmailMultiAlternatives

from celery import shared_task
from new_portal.models import Post


@shared_task
def with_every_new_post(pk):
    """Вызывается в сигнале, при создании новой публикации и выполняет рассылку всем подписчикам категории."""

    post = Post.objects.get(pk=pk)
    categories = post.categories.all()                            # Получаем все категории, связанные с созданным постом
    emails = set()                                                # Используем set для уникальности email-адресов

    # Получаем email-адреса пользователей, подписанных на категорию созданного поста
    for category in categories:
        category_emails = User.objects.filter(subscriptions__category=category).values_list('email', flat=True)
        emails.update(category_emails)                            # Добавляем email-адреса в set

    subject = f'Новая запись в категории {" ,".join(cat.name for cat in post.categories.all())}'

    text_content = (
        f'Название: {post.title}\n'
        f'Анонс: {post.preview()}\n\n'
        f'Ссылка на публикацию: {settings.SITE_URL}{post.get_absolute_url()}'
    )

    html_content = (
        f'Название: {post.title}<br>'
        f'Анонс: {post.preview()}<br><br>'
        f'<a href="{settings.SITE_URL}{post.get_absolute_url()}">'
        f'Ссылка на публикацию</a>'
    )

    for email in emails:
        msg = EmailMultiAlternatives(subject, text_content, None, [email])
        msg.attach_alternative(html_content, "text/html")
        msg.send()
