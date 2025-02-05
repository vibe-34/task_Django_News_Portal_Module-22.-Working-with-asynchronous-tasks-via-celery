import os                                            # импортируем библиотеку для взаимодействия с операционной системой
from celery import Celery                            # импортируем библиотеку Celery
from celery.schedules import crontab

# связываем настройки Django с настройками Celery через переменную окружения
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'project.settings')

# создаем экземпляр приложения Celery
app = Celery('project')

# Устанавливаем для него файл конфигурации. Мы также указываем пространство имен, чтобы Celery сам находил все
# необходимые настройки в общем конфигурационном файле settings.py. Он их будет искать по шаблону «CELERY_***»
app.config_from_object('django.conf:settings', namespace='CELERY')

# указываем Celery автоматически искать задания в файлах tasks.py каждого приложения проекта
app.autodiscover_tasks()

# для автоматической попытке установить соединение с брокером, если оно не удается при первом запуске.
app.conf.broker_connection_retry_on_startup = True

# отправлять уведомления каждый понедельник в 8 утра, о новых публикациях (подписчикам категорий)
app.conf.beat_schedule = {
    'send_notification_every_monday_8am': {
        'task': 'new_portal.tasks.weekly_newsletter',
        'schedule': crontab(hour=8, minute=0, day_of_week='monday'),
    },
}
