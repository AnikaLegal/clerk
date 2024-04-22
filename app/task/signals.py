from django.db.models.signals import post_save
from django.dispatch import receiver
from django_q.tasks import async_task

from core.models.issue_event import IssueEvent
from .tasks import create_tasks


@receiver(post_save, sender=IssueEvent)
def post_save_issue_event(sender, instance, **kwargs):
    """
    Potentially trigger task creation when specific issue events occur.
    """
    event: IssueEvent = instance
    async_task(create_tasks, event.pk)
