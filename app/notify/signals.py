import logging

from django.db.models.signals import pre_save
from django.dispatch import receiver
from django_q.tasks import async_task

from core.models import Issue
from notify.models import Notification, NotifyEvent, NotifyTarget, NotifyChannel
from slack.services import (
    send_slack_direct_message,
    get_slack_user_by_email,
)

logger = logging.getLogger(__name__)


@receiver(pre_save, sender=Issue)
def pre_save_issue(sender, instance, **kwargs):
    """
    Detect state changes for notifications
    """
    issue = instance
    if not issue.pk:
        return

    try:
        prev_issue = Issue.objects.get(pk=issue.pk)
    except Issue.DoesNotExist:
        return

    if issue.stage != prev_issue.stage:
        logger.info(
            "Dispatching notification stage change task for Issue[%s]", issue.pk
        )
        async_task(on_issue_stage_change, issue.pk, prev_issue.stage, issue.stage)


def on_issue_stage_change(issue_pk, old_stage: str, new_stage: str):
    issue = Issue.objects.get(pk=issue_pk)
    notifications = Notification.objects.filter(
        event=NotifyEvent.STAGE_CHANGE, event_stage=new_stage
    )
    for notification in notifications:
        if not notification.channel == NotifyChannel.SLACK:
            logger.error("Notification[%s] has unsupported channel", notification)
            continue

        email = None
        if notification.target == NotifyTarget.PARALEGAL:
            email = issue.paralegal and issue.paralegal.email
        elif notification.target == NotifyTarget.LAWYER:
            email = issue.lawyer and issue.lawyer.email

        if not email:
            logger.error(
                "No matching email found for Notification[%s] and Issue[%s]",
                notification.pk,
                issue_pk,
            )
            continue

        logger.info(
            "Sending Notification[%s] to %s for Issue[%s]",
            notification.pk,
            email,
            issue_pk,
        )
        slack_user = get_slack_user_by_email(email)
        if not slack_user:
            logger.error(
                "Slack user not found while sending Notification[%s] to %s for Issue[%s]",
                notification.pk,
                email,
                issue_pk,
            )
            continue

        message_text = f"*Notification for case <{issue.url}|{issue.fileref}>*\n{notification.message_text}"
        send_slack_direct_message(message_text, slack_user["id"])
