import os
import logging
from typing import List, Tuple
from django.core.mail import EmailMultiAlternatives
from django.conf import settings
from django.utils import timezone

from core.models import IssueNote
from core.models.issue_note import NoteType
from emails.models import Email, EmailState
from utils.sentry import WithSentryCapture


logger = logging.getLogger(__name__)


EMAIL_SEND_RULES = (
    (lambda e: bool(e.issue), "no related Issue."),
    (lambda e: e.state == EmailState.READY_TO_SEND, "not ready to send."),
)


def _send_email_task(email_pk: int):
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

    from_addr = build_clerk_address(email.issue)
    attachments = []
    for att in email.emailattachment_set.all():
        file_name = os.path.basename(att.file.name)
        file_bytes = att.file.read()
        attachments.append((file_name, file_bytes, att.content_type))

    send_email(
        from_addr,
        email.to_address,
        email.cc_addresses,
        email.subject,
        email.text,
        attachments,
    )
    IssueNote.objects.create(
        issue=email.issue,
        note_type=NoteType.EMAIL,
        content_object=email,
        text=email.get_sent_note_text(),
    )
    Email.objects.filter(pk=email_pk).update(
        state=EmailState.SENT, processed_at=timezone.now()
    )


send_email_task = WithSentryCapture(_send_email_task)


def send_email(
    from_addr: str,
    to_addr: str,
    cc_addrs: List[str],
    subject: str,
    body: str,
    attachments: List[Tuple[str, bytes, str]] = None,
):
    """
    FIXME: TEST ME.
    Send an email.
    https://docs.djangoproject.com/en/3.2/topics/email/#django.core.mail.EmailMessage
    https://docs.djangoproject.com/en/3.2/topics/email/#sending-alternative-content-types
    """
    logger.info("Sending email to %s from %s", to_addr, from_addr)
    email = EmailMultiAlternatives(
        subject=subject,
        body=body,
        from_email=from_addr,
        to=[to_addr],
        cc=cc_addrs,
        attachments=attachments,
        # TODO: BCC? Reply to?
    )
    email.send(fail_silently=False)


def build_clerk_address(issue, email_only=False):
    """
    FIXME: TEST ME.
    """
    issue_prefix = str(issue.id).split("-")[0]
    email = f"case.{issue_prefix}@{settings.EMAIL_DOMAIN}"
    return email if email_only else f"Anika Legal <{email}>"
