from .celery import app as celery_app

# согласно рекомендации из документации к Celery, мы должны добавить эту настройку
__all__ = ('celery_app',)
