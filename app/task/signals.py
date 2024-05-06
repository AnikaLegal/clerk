from django.db.models.signals import post_save
from django.dispatch import receiver
from django_q.tasks import async_task

from core.models import IssueEvent
from .tasks import maybe_create_tasks


@receiver(post_save, sender=IssueEvent)
def post_save_issue_event(sender, instance, **kwargs):
    event: IssueEvent = instance
    async_task(maybe_create_tasks, event.pk)
