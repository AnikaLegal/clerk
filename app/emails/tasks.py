import os
import logging

from utils.sentry import WithSentryCapture
from core.models import IssueNote
from core.models.issue_note import NoteType
from .models import Email, EmailState
from .service import send_email, build_clerk_address, parse_clerk_address

logger = logging.getLogger(__name__)


EMAIL_SEND_RULES = (
    (lambda e: bool(e.issue), "no related Issue."),
    (lambda e: e.state == EmailState.READY_TO_SEND, "not ready to send."),
)


def _send_email_task(email_pk: int):
    """
    Sends an email that is ready to be sent.
    FIXME: TEST ME
    """
    email = (
        Email.objects.select_related("issue", "sender")
        .prefetch_related("emailattachment_set")
        .get(pk=email_pk)
    )
    for rule, msg in EMAIL_SEND_RULES:
        if not rule(email):
            logger.error(f"Cannot sent Email[{email_pk}]: {msg}")
            return

    from_addr = build_clerk_address(email)
    attachments = []
    for att in email.emailattachment_set.all():
        file_name = os.path.basename(att.file.name)
        file_bytes = att.file.read()
        attachments.append((file_name, file_bytes, att.content_type))

    send_email(from_addr, email.to_addr, email.subject, email.text, attachments)
    IssueNote.objects.create(
        issue=email.issue,
        note_type=NoteType.EMAIL,
        content_object=email,
        text=email.get_sent_note_text(),
    )
    Email.objects.filter(pk=email_pk).update(state=EmailState.SENT)


send_email_task = WithSentryCapture(_send_email_task)


EMAIL_RECEIVE_RULES = (
    (lambda e: e.state == EmailState.RECEIVED, "not in 'received' state."),
)


def _receive_email_task(email_pk: int):
    """
    Ingests an received emails and attempts to associate them with related issues.
    Run as a scheduled task.
    FIXME: TEST ME
    """
    email = Email.objects.get(pk=email_pk)
    for rule, msg in EMAIL_RECEIVE_RULES:
        if not rule(email):
            logger.error(f"Cannot ingest Email[{email_pk}]: {msg}")
            return

    to_addr, issue_pk = parse_clerk_address(email)
    if to_addr and issue_pk:
        IssueNote.objects.create(
            issue=email.issue,
            note_type=NoteType.EMAIL,
            content_object=email,
            text=email.get_received_note_text(),
        )
        Email.objects.filter(pk=email_pk).update(
            to_addr=to_addr, issue_id=issue_pk, state=EmailState.INGESTED
        )


receive_email_task = WithSentryCapture(_receive_email_task)
