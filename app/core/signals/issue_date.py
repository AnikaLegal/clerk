import logging

from auditlog.models import LogEntry
from auditlog.signals import post_log
from core.models import AuditEvent, IssueDate, IssueNote
from core.models.issue_note import NoteType
from django.db import transaction
from django.dispatch import receiver
from django_q.tasks import async_task, result

logger = logging.getLogger(__name__)


@receiver(post_log, sender=IssueDate)
def post_log_task(log_entry, instance, error, **kwargs):
    if error:
        logger.exception(error)
    else:
        # Wait on the result for a little bit so we can update the frontend UI
        # immediately. We could, of course, just run the task synchronously, i.e.
        # without using async_task, but then if the task fails it is difficult to
        # rerun the same task again.
        transaction.on_commit(
            lambda: result(
                async_task(handle_issue_date_log, log_entry.pk, instance.issue_id),
                wait=2000,
            )
        )


def handle_issue_date_log(log_entry_pk: int, issue_id):
    log_entry = LogEntry.objects.get(pk=log_entry_pk)
    with transaction.atomic():
        audit_event = AuditEvent.objects.create(log_entry=log_entry)
        IssueNote.objects.create(
            note_type=NoteType.EVENT,
            issue_id=issue_id,
            content_object=audit_event,
            created_at=log_entry.timestamp,
        )
    return True
