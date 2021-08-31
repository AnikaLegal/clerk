import logging

from django.utils.datastructures import MultiValueDict
from django.db import transaction

from utils.sentry import WithSentryCapture
from core.models import IssueNote
from core.models.issue_note import NoteType
from emails.models import Email, EmailAttachment, EmailState
from .utils import parse_clerk_address

logger = logging.getLogger(__name__)


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


def save_inbound_email(data: MultiValueDict, files: MultiValueDict):
    """
    Parse an inbound email from SendGrid and save as an Email.
    """
    email_data = {
        "received_data": data,
        "state": EmailState.RECEIVED,
    }
    with transaction.atomic():
        email = Email.objects.create(**email_data)
        # FIXME: Mangles non-ASCII UTF-8 text.
        for key, file in files.values():
            file = files[key]
            EmailAttachment.objects.create(
                email=email, file=file, content_type=file.content_type
            )
