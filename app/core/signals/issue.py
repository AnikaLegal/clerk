import logging

from django.db.models.signals import post_save
from django.dispatch import receiver
from django_q.tasks import async_task

from core.models import Issue
from core.services.slack import send_issue_slack
from actionstep.services.actionstep import send_issue_actionstep

logger = logging.getLogger(__name__)


@receiver(post_save, sender=Issue)
def save_issue(sender, instance, **kwargs):
    issue = instance
    if not issue.is_alert_sent:
        logger.info("Dispatching alert task for Issue<%s]>", issue.id)
        async_task(send_issue_slack, str(issue.pk))
    if not issue.is_case_sent:
        logger.info("Dispatching Actionstep task for Issue<%s]>", issue.id)
        async_task(send_issue_actionstep, str(issue.pk))
