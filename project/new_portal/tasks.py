from celery import shared_task
# from datetime import datetime, timedelta
from django.conf import settings
from django.core.mail import EmailMultiAlternatives
# from django.template.loader import render_to_string
# from unicodedata import category
# from news.models import Category, Subscription


@shared_task
def with_every_new_post(category, preview, title, emails, get_absolute_url):
    """Вызывается в сигнале, при создании новой публикации и выполняет рассылку всем подписчикам категории."""

    subject = f'Новая запись в категории {category}'

    text_content = (
        f'Название: {title}\n'
        f'Анонс: {preview}\n\n'
        f'Ссылка на публикацию: {settings.SITE_URL}{get_absolute_url}'
    )

    html_content = (
        f'Название: {title}<br>'
        f'Анонс: {preview}<br><br>'
        f'<a href="{settings.SITE_URL}{get_absolute_url}">'
        f'Ссылка на публикацию</a>'
    )

    for email in emails:
        msg = EmailMultiAlternatives(subject, text_content, None, [email])
        msg.attach_alternative(html_content, "text/html")
        msg.send()
