from django.contrib import admin

from .models import TaskMeta


@admin.register(TaskMeta)
class TaskMetaAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'status', 'started', 'last_updated', 'completed',)
    list_filter = ('status',)
