from django.contrib.auth.models import User
from django.core.mail import EmailMultiAlternatives
from django.db.models.signals import m2m_changed
from django.dispatch import receiver

from .models import PostCategory
from django.conf import settings


@receiver(m2m_changed, sender=PostCategory)                      # instance будет по модели Post
def post_created(sender, instance, action, **kwargs):
    """
    Автоматическая отправка уведомлений пользователям по e-mail
    о создании новых постов в категориях, на которые они подписаны.
    """

    if action == 'post_add':                                      # Проверяем, что действие - добавление поста
        categories = instance.categories.all()                    # Получаем все категории, связанные с созданным постом
        emails = set()                                            # Используем set для уникальности email-адресов

        # Получаем email-адреса пользователей, подписанных на категорию созданного поста
        for category in categories:
            category_emails = User.objects.filter(subscriptions__category=category).values_list('email', flat=True)
            emails.update(category_emails)                        # Добавляем email-адреса в set

        # Создание содержимого письма
        if emails:
            subject = f'Новая запись в категории: {", ".join([cat.name for cat in categories])}'
            text_content = (
                f'Название: {instance.title}\n'
                f'Анонс: {instance.content[:50]}...\n\n'
                f'Ссылка на публикацию: {settings.SITE_URL}{instance.get_absolute_url()}'
            )
            html_content = (
                f'Название: {instance.title}<br>'
                f'Анонс: {instance.content[:50]}...<br><br>'
                f'<a href="{settings.SITE_URL}{instance.get_absolute_url()}">'
                f'Ссылка на публикацию</a>'
            )

            # Отправка писем
            for email in emails:
                msg = EmailMultiAlternatives(subject, text_content, None, [email])
                msg.attach_alternative(html_content, "text/html")
                msg.send()
