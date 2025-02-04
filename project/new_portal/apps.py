from django.apps import AppConfig


class NewPortalConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'new_portal'

    def ready(self):
        from . import signals  # выполнение модуля -> регистрация сигналов
