import logging

from django.conf import settings
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django_q.tasks import async_task

from actionstep.services.actionstep import send_issue_actionstep
from core.models import Issue, IssueEvent
from core.services.slack import send_issue_slack

logger = logging.getLogger(__name__)


@receiver(pre_save, sender=Issue)
def pre_save_issue(sender, instance, **kwargs):
    """
    Detect state changes and create IssueEvents as required.
    This arguably belongs in the Issue.save() method coz then we could do atomic transactions.
    """
    issue = instance
    if not issue.pk:
        return

    try:
        prev_issue = Issue.objects.get(pk=issue.pk)
    except Issue.DoesNotExist:
        return

    IssueEvent.maybe_generate_event(issue, prev_issue)


@receiver(post_save, sender=Issue)
def post_save_issue(sender, instance, **kwargs):
    issue = instance
    if not issue.is_alert_sent:
        logger.info("Dispatching alert task for Issue<%s]>", issue.id)
        async_task(send_issue_slack, str(issue.pk))
    if settings.ACTIONSTEP_SYNC and not issue.is_case_sent:
        logger.info("Dispatching Actionstep task for Issue<%s]>", issue.id)
        async_task(send_issue_actionstep, str(issue.pk))
