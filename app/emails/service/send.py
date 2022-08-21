import os
import logging
from django.conf import settings
from django.utils import timezone

from core.models import IssueNote
from core.models.issue_note import NoteType
from emails.models import Email, EmailState
from utils.sentry import sentry_task
from emails.api import send_email

logger = logging.getLogger(__name__)


EMAIL_SEND_RULES = (
    (lambda e: e.state == EmailState.READY_TO_SEND, "not ready to send."),
)


@sentry_task
def send_email_task(email_pk: int):
    """
    Sends an email that is ready to be sent.
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

    from_addr = email.from_address
    attachments = []
    if email.issue:
        from_addr = build_clerk_address(email.issue, email_only=True)
        for att in email.emailattachment_set.all():
            file_name = os.path.basename(att.file.name)
            file_bytes = att.file.read()
            attachments.append((file_name, file_bytes, att.content_type))

    logger.info("Sending email to %s from %s", email.to_address, from_addr)
    message_id = send_email(
        from_addr,
        email.to_address,
        email.cc_addresses,
        email.subject,
        email.text,
        attachments,
        html=email.html,
    )
    Email.objects.filter(pk=email_pk).update(
        state=EmailState.SENT,
        processed_at=timezone.now(),
        sendgrid_id=message_id,
    )
    if email.issue:
        IssueNote.objects.create(
            issue=email.issue,
            note_type=NoteType.EMAIL,
            content_object=email,
            text=email.get_sent_note_text(),
        )


def build_clerk_address(issue, email_only=False):
    """
    FIXME: TEST ME.
    """
    issue_prefix = str(issue.id).split("-")[0]
    email = f"case.{issue_prefix}@{settings.EMAIL_DOMAIN}"
    return email if email_only else f"Anika Legal <{email}>"
