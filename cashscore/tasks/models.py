from django.contrib.postgres.fields import JSONField
from django.db import models
from django.utils import timezone

from celery import states


class TaskMetaManager(models.Manager):
    def store_result(self, task_id, result, status, 
            task_name=None, task_args=None, task_kwargs=None,
            worker=None, meta=None, traceback=None, using=None):
        fields = {
            'id': task_id,
            'result': result,
            'status': status,
            'name': task_name,
            'args': task_args,
            'kwargs': task_kwargs,
            'worker': worker,
            'meta': meta,
            'traceback': traceback,
        }

        if status == states.SUCCESS:
            fields['completed'] = timezone.now()

        obj, created = self.using(using).get_or_create(
            id=task_id, defaults=fields)

        if not created:
            for k, v in fields.items():
                setattr(obj, k, v)
            obj.save(using=using)

        return obj


ALL_STATES = sorted(states.ALL_STATES)
CELERY_STATE_CHOICES = sorted(zip(ALL_STATES, ALL_STATES))


class TaskMeta(models.Model):
    id = models.CharField(max_length=255, unique=True, primary_key=True)
    result = models.TextField(null=True, editable=False)
    status = models.CharField(max_length=50, choices=CELERY_STATE_CHOICES)
    name = models.CharField(max_length=255, null=True)
    args = JSONField(null=True)
    kwargs = JSONField(null=True)
    worker = models.CharField(max_length=100, null=True)

    started = models.DateTimeField(auto_now_add=True)
    last_updated = models.DateTimeField(auto_now=True)
    completed = models.DateTimeField(null=True)

    traceback = models.TextField(null=True)
    meta = JSONField(null=True, editable=False)

    objects = TaskMetaManager()
