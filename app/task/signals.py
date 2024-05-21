from django.db.models.signals import post_save
from django.dispatch import receiver
from django_q.tasks import async_task
from django.db import transaction

from task.models import Task
from core.models import IssueEvent
from .tasks import handle_event, handle_task


@receiver(post_save, sender=IssueEvent)
def post_save_issue_event(sender, instance, **kwargs):
    event: IssueEvent = instance
    transaction.on_commit(lambda: async_task(handle_event, event.pk))


@receiver(post_save, sender=Task)
def post_save_task(sender, instance, **kwargs):
    task: Task = instance
    transaction.on_commit(lambda: async_task(handle_task, task.pk))
