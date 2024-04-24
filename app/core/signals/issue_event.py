import logging

from django.db.models.signals import post_save
from django.dispatch import receiver

from core.models import IssueEvent, IssueNote
from core.models.issue_note import NoteType
from core.models.issue_event import EventType

logger = logging.getLogger(__name__)


@receiver(post_save, sender=IssueEvent)
def post_save_issue_event(sender, instance, **kwargs):
    event: IssueEvent = instance

    if event.event_type != EventType.CREATE:
        IssueNote.objects.create(
            issue=event.issue,
            note_type=NoteType.EVENT,
            content_object=event,
        )
