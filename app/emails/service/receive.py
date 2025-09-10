import json
import logging
from os.path import basename

from core.models import Issue, IssueNote
from core.models.issue_note import NoteType
from django.conf import settings
from django.core.files import File
from django.db import transaction
from django.utils import timezone
from django.utils.datastructures import MultiValueDict
from emails.models import (
    Email,
    EmailAttachment,
    EmailState,
    ReceivedAttachment,
    ReceivedEmail,
)
from utils.sentry import sentry_task

logger = logging.getLogger(__name__)


EMAIL_RECEIVE_RULES = (
    (
        lambda e: e.state in [EmailState.RECEIVED, EmailState.INGEST_FAILURE],
        "not in 'received' or 'failure' state.",
    ),
)


def save_inbound_email(data: MultiValueDict, files: MultiValueDict):
    """
    Save inbound email data for processing later.
    """
    with transaction.atomic():
        email = ReceivedEmail.objects.create(received_data=data)
        for file in files.values():
            ReceivedAttachment.objects.create(
                email=email, file=file, name=file.name, content_type=file.content_type
            )


@sentry_task
def receive_email_task(email_pk: int):
    """
    Process received email data.
    """
    received_email = ReceivedEmail.objects.get(pk=email_pk)
    with transaction.atomic():
        email = Email.objects.create(
            received_data=received_email.received_data, state=EmailState.RECEIVED
        )
        for received_attachment in received_email.attachments.all():
            file = File(
                received_attachment.file.file,
                name=received_attachment.name,
            )
            EmailAttachment.objects.create(
                email=email,
                file=file,
                content_type=received_attachment.content_type,
            )
    received_email.delete()


@sentry_task
def ingest_email_task(email_pk: int):
    """
    Ingests a received email and attempts to associate it with a case.
    """
    email = Email.objects.get(pk=email_pk)
    for rule, msg in EMAIL_RECEIVE_RULES:
        if not rule(email):
            logger.error(f"Cannot ingest Email[{email_pk}]: {msg}")
            return

    parsed_data = None
    try:
        if email.received_data:
            parsed_data = parse_received_data(email.received_data)
    except Exception:
        pass

    if parsed_data:
        email.state = EmailState.INGESTED
        email.issue = parsed_data["issue"]
        email.from_address = parsed_data["from_address"]
        email.to_address = parsed_data["to_address"]
        email.cc_addresses = parsed_data["cc_addresses"]
        email.subject = parsed_data["subject"]
        email.text = parsed_data["text"]
        email.html = parsed_data["html"]
        email.processed_at = timezone.now()
        email.save()
        IssueNote.objects.create(
            issue=parsed_data["issue"],
            created_at=email.created_at,
            note_type=NoteType.EMAIL,
            content_object=email,
            text=email.get_received_note_text(),
        )
    else:
        logger.error(f"Cannot ingest Email[{email_pk}]: Parsing failure")
        email.state = EmailState.INGEST_FAILURE
        email.save()


def parse_received_data(email_data: dict) -> dict | None:
    """
    Returns the parsed email data as a dict or None
    data is in format: {
        subject: str
        text: str
        from_address: str
        to_address: str
        cc_addresses: List[str],
        issue: Issue
    }
    """
    parsed_data = {}
    # Find who the email is to.
    envelope = json.loads(email_data["envelope"])
    to_addrs = envelope["to"]
    if len(to_addrs) != 1:
        return None

    to_addr = clean_email_addr(to_addrs[0])
    parsed_data["to_address"] = to_addr
    parsed_data["from_address"] = envelope["from"]

    cc_addrs = []
    cc_addr_strs = email_data.get("cc", "").split(",")
    to_addr_strs = email_data["to"].split(",")
    for addr_str in cc_addr_strs + to_addr_strs:
        addr_cleaned = clean_email_addr(addr_str)
        if addr_cleaned and addr_cleaned != parsed_data["to_address"]:
            cc_addrs.append(addr_cleaned)

    parsed_data["cc_addresses"] = cc_addrs
    parsed_data["text"] = email_data.get("text", "")
    parsed_data["subject"] = email_data["subject"]
    parsed_data["html"] = email_data.get("html", "")

    # Try find the issue from to_addr.
    user, domain = to_addr.split("@")
    if domain != settings.EMAIL_DOMAIN:
        logger.exception(f"Incorrect domain in to address {to_addr}")
        return None

    try:
        user_parts = user.split(".")
        issue_prefix = user_parts[-1]
        parsed_data["issue"] = Issue.objects.get(id__startswith=issue_prefix)
    except Exception:
        logger.exception(f"Could not parse email address {to_addr}")
        return None

    return parsed_data


def clean_email_addr(email_addr):
    email_addr = email_addr.strip()
    if "<" in email_addr:
        return email_addr.split("<")[1].rstrip(">")
    else:
        return email_addr.strip()
