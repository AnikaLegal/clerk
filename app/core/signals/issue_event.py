import logging

from accounts import events as accounts_events
from core.models import IssueEvent
from core.models.issue_event import EventType
from core.services.slack import send_case_assignment_slack
from django.db.models.signals import post_save
from django.dispatch import receiver

logger = logging.getLogger(__name__)


@receiver(post_save, sender=IssueEvent)
def post_save_issue_event(sender, instance, **kwargs):
    event: IssueEvent = instance

    if event.event_type == EventType.PARALEGAL or event.event_type == EventType.LAWYER:
        if event.prev_user:
            accounts_events.user_removed_from_case.send(
                sender=IssueEvent, user=event.prev_user, issue=event.issue
            )
        if event.next_user:
            accounts_events.user_added_to_case.send(
                sender=IssueEvent, user=event.next_user, issue=event.issue
            )

            # Notify paralegal of case assignment.
            if event.event_type == EventType.PARALEGAL:
                send_case_assignment_slack(event.issue)
