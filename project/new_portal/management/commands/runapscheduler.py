import logging

from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.cron import CronTrigger
from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.core.management.base import BaseCommand
from django.template.loader import render_to_string
from django_apscheduler import util
from django_apscheduler.jobstores import DjangoJobStore
from django_apscheduler.models import DjangoJobExecution
from django.utils import timezone
from datetime import timedelta

from new_portal.models import Category, Subscription

logger = logging.getLogger(__name__)


def my_job():
    # Текущая дата и время
    now = timezone.now()
    week_ago = now - timedelta(days=7)

    # Перебираем все категории
    for category in Category.objects.all():

        # Получаем email подписчиков по категориям
        subscribers = list(Subscription.objects.filter(category=category).values_list('user__email', flat=True))

        # Получаем публикации по категориям за последние 7 дней
        posts_list = list(category.post_set.filter(time_in__gte=week_ago))

        # Если есть подписчики и публикации, отправляем письма
        if subscribers and posts_list:
            for email in subscribers:

                # Генерируем HTML контент для письма
                html_content = render_to_string(
                    'email/daily_post.html',
                    {
                        'link': settings.SITE_URL,
                        'posts_list': posts_list,
                    }
                )

                # Создаем и отправляем email
                msg = EmailMultiAlternatives(
                    subject='Публикации за неделю',
                    body='',                               # Текстовое содержимое (можно оставить пустым, если не нужно)
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    to=[email],
                )
                msg.attach_alternative(html_content, 'text/html')
                msg.send()


# функция, которая будет удалять неактуальные задачи
@util.close_old_connections
def delete_old_job_executions(max_age=604_800):
    DjangoJobExecution.objects.delete_old_job_executions(max_age)


class Command(BaseCommand):
    help = "Runs APScheduler."

    def handle(self, *args, **options):
        scheduler = BlockingScheduler(timezone=settings.TIME_ZONE)
        scheduler.add_jobstore(DjangoJobStore(), "default")

        # добавляем работу задачнику.
        scheduler.add_job(
            my_job,
            trigger=CronTrigger(day_of_week="fri", hour="18", minute="00"),
            # trigger=CronTrigger(second='*/10'),                         # строка для теста (рассылка каждые 10 секунд)
            id="my_job",                                                  # уникальный id
            max_instances=1,
            replace_existing=True,
        )
        logger.info("Added job 'my_job'.")

        scheduler.add_job(
            delete_old_job_executions,
            trigger=CronTrigger(
                day_of_week="mon", hour="00", minute="00"
            ),
            # каждую неделю будут удаляться старые задачи, которые не удалось выполнить или выполнять уже не надо
            id="delete_old_job_executions",
            max_instances=1,
            replace_existing=True,
        )
        logger.info("Added weekly job: 'delete_old_job_executions'.")

        try:
            logger.info("Starting scheduler...")
            scheduler.start()
        except KeyboardInterrupt:
            logger.info("Stopping scheduler...")
            scheduler.shutdown()
            logger.info("Scheduler shut down successfully!")
