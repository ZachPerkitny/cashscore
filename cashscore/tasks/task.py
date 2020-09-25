from django.db import transaction

import celery
from kombu.utils.uuid import uuid

from .models import TaskMeta


class Task(celery.Task):
    def apply_async(self, args=None, kwargs=None, task_id=None, producer=None,
            link=None, link_error=None, shadow=None, **options):
        task_id = task_id or uuid()
        self.update_state(task_id, celery.states.PENDING)
        return transaction.on_commit(
            lambda: super(Task, self).apply_async(
                args, kwargs, task_id, producer, link,
                link_error, shadow, **options)
        )

    def delay(self, *args, **kwargs):
        task_id = uuid()
        self.update_state(task_id, celery.states.PENDING)
        return transaction.on_commit(
            lambda: super(Task, self).apply_async(args, kwargs, task_id)
        )
