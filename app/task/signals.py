import logging

from auditlog.signals import post_log
from core.models import IssueEvent
from django.db import transaction
from django.db.models.signals import post_save
from django.dispatch import receiver
from django_q.tasks import async_task
from task.models import (
    Task,
    TaskActivity,
    TaskComment,
    TaskEvent,
    TaskRequest,
)

from .tasks import (
    handle_event_save,
    handle_task_log,
    handle_task_request_log,
    handle_task_save,
)

logger = logging.getLogger(__name__)


@receiver(post_save, sender=IssueEvent)
def post_save_issue_event(instance, **kwargs):
    event: IssueEvent = instance
    transaction.on_commit(lambda: async_task(handle_event_save, event.pk))


@receiver(post_save, sender=Task)
def post_save_task(instance, **kwargs):
    task: Task = instance
    transaction.on_commit(lambda: async_task(handle_task_save, task.pk))


@receiver(post_log, sender=Task)
def post_log_task(log_entry, error, **kwargs):
    if error:
        logger.exception(error)
    else:
        transaction.on_commit(lambda: async_task(handle_task_log, log_entry.pk))


@receiver(post_log, sender=TaskRequest)
def post_log_task_request(log_entry, error, **kwargs):
    if error:
        logger.exception(error)
    else:
        transaction.on_commit(lambda: async_task(handle_task_request_log, log_entry.pk))


@receiver(post_save, sender=TaskComment)
def post_save_task_comment(instance, created, **kwargs):
    if created:
        TaskActivity.objects.create(content_object=instance)


@receiver(post_save, sender=TaskEvent)
def post_save_task_event(instance, created, **kwargs):
    if created:
        TaskActivity.objects.create(content_object=instance)
