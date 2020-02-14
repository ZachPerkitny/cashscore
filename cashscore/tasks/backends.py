from django.forms.models import model_to_dict

from celery.backends.base import BaseDictBackend

from .models import TaskMeta


class DatabaseBackend(BaseDictBackend):
    def _store_result(self, task_id, result, status,
            traceback=None, request=None, using=None):
        name = getattr(request, 'task', None) if request else None
        args = getattr(request, 'argsrepr', getattr(request, 'args', None))
        kwargs = getattr(request, 'kwargsrepr', getattr(request, 'kwargs', None))
        worker = getattr(request, 'hostname', None)

        TaskMeta.objects.store_result(
            task_id,
            result,
            status,
            task_name=name,
            task_args=args,
            task_kwargs=kwargs,
            worker=worker,
            traceback=traceback,
            meta={
                'children': self.current_task_children(request),
            },
            using=using)

        return result
