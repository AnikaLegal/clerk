import logging

from core.models import IssueEvent
from core.models.issue_event import EventType
from core.services.slack import send_case_assignment_slack
from django.db.models.signals import post_save
from django.dispatch import receiver
from microsoft.service import add_user_to_case, remove_user_from_case

logger = logging.getLogger(__name__)


@receiver(post_save, sender=IssueEvent)
def post_save_issue_event(sender, instance, **kwargs):
    event: IssueEvent = instance

    # Adjust Sharepoint access permissions.
    if event.event_type == EventType.PARALEGAL or event.event_type == EventType.LAWYER:
        if event.prev_user:
            # Remove Sharepoint access permissions.
            remove_user_from_case(event.prev_user, event.issue)
        if event.next_user:
            # Add Sharepoint access permissions.
            add_user_to_case(event.next_user, event.issue)

            # Notify paralegal of case assignment.
            if event.event_type == EventType.PARALEGAL:
                send_case_assignment_slack(event.issue)
