import os

from celery import Celery


os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cashscore.config.settings.local')

app = Celery('cashscore', task_cls='cashscore.tasks.task:Task')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()
