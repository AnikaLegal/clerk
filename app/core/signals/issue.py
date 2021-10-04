import logging

from django.conf import settings
from django.db.models.signals import pre_save, post_save
from django.dispatch import receiver
from django_q.tasks import async_task

from actionstep.services.actionstep import send_issue_actionstep
from core.models import Issue, IssueEvent
from core.services.slack import send_issue_slack
from microsoft.tasks import set_up_new_case_task
from microsoft.service import add_user_to_case, remove_user_from_case

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

    # If the paralegal for the current Issue object is different from that in the database.
    # We need to update the matching folder on Sharepoint by removing the old paralegal and adding the new one.
    if issue.paralegal != prev_issue.paralegal:
        if prev_issue.paralegal:
            logger.info(
                "Removing User<%s> from the Sharepoint folder matching Issue<%s>",
                prev_issue.paralegal.id,
                prev_issue.id,
            )
            remove_user_from_case(prev_issue.paralegal, prev_issue)

        if issue.paralegal:
            logger.info(
                "Adding User<%s> to the Sharepoint folder matching Issue<%s>",
                issue.paralegal.id,
                issue.id,
            )
            add_user_to_case(issue.paralegal, issue)


@receiver(post_save, sender=Issue)
def post_save_issue(sender, instance, **kwargs):
    issue = instance
    if not issue.is_alert_sent:
        logger.info("Dispatching alert task for Issue<%s>", issue.id)
        async_task(send_issue_slack, str(issue.pk))
    if not issue.is_sharepoint_set_up:
        logger.info("Dispatching Sharepoint task for Issue<%s>", issue.id)
        async_task(set_up_new_case_task, str(issue.pk))
    if settings.ACTIONSTEP_SYNC and not issue.is_case_sent:
        logger.info("Dispatching Actionstep task for Issue<%s>", issue.id)
        async_task(send_issue_actionstep, str(issue.pk))
