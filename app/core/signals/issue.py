import logging

from django.db.models.signals import pre_save, post_save
from django.dispatch import receiver
from django_q.tasks import async_task

from core.models import Issue, IssueEvent
from core.services.slack import send_issue_slack
from emails.service.welcome import send_welcome_email
from microsoft.tasks import set_up_new_case_task

logger = logging.getLogger(__name__)


@receiver(pre_save, sender=Issue)
def pre_save_issue(sender, instance, **kwargs):
    """
    Detect state changes and create IssueEvents as required.
    """
    issue: Issue = instance
    if not issue.pk:
        return

    try:
        prev_issue = Issue.objects.get(pk=issue.pk)
    except Issue.DoesNotExist:
        prev_issue = None

    IssueEvent.maybe_generate_event(issue, prev_issue)


@receiver(post_save, sender=Issue)
def post_save_issue(sender, instance, **kwargs):
    issue = instance
    if not issue.is_alert_sent:
        logger.info("Dispatching alert task for Issue<%s>", issue.id)
        async_task(send_issue_slack, str(issue.pk))
    if not issue.is_sharepoint_set_up:
        logger.info("Dispatching Sharepoint task for Issue<%s>", issue.id)
        async_task(set_up_new_case_task, str(issue.pk))
    if not issue.is_welcome_email_sent:
        logger.info("Dispatching welcome email task for Issue<%s>", issue.id)
        async_task(send_welcome_email, str(issue.pk))
