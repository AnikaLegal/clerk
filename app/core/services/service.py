import logging

from core.models import ServiceEvent
from core.models.issue_note import IssueNote, NoteType

logger = logging.getLogger(__file__)


def update_timeline(service_event_pk: int) -> bool:
    service_event = ServiceEvent.objects.get(pk=service_event_pk)
    IssueNote.objects.create(
        note_type=NoteType.EVENT,
        issue=service_event.service.issue,
        content_object=service_event,
        created_at=service_event.created_at,
    )
    return True
