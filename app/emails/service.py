import json
import logging
from typing import List, Tuple
from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.utils.datastructures import MultiValueDict
from django.db import transaction

from core.models import Issue
from .models import Email, EmailAttachment, EmailState

logger = logging.getLogger(__name__)


def build_clerk_address(email: Email):
    """
    FIXME: TEST ME.
    """
    assert email.issue
    issue_prefix = str(email.issue.id).split("-")[0]
    email = f"case.{issue_prefix}@{settings.EMAIL_DOMAIN}"
    return f"Anika Legal <{email}>"


def parse_clerk_address(email: Email) -> Tuple[str, Issue]:
    """
    Returns to address and issue or None, None
    FIXME: TEST ME.
    """
    assert False, "TODO"
    # FIXME: BROKEN

    user, domain = email_addr.split("@")
    assert domain == settings.EMAIL_DOMAIN, f"Incorrect domain {domain}"

    try:
        user_parts = user.split(".")
        issue_prefix = user_parts[-1]
        return Issue.objects.get(id__startswith=issue_prefix)
    except:
        logger.exception(f"Could not parse email address {email_addr}")


def send_email(
    from_addr: str,
    to_addr: str,
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
        attachments=attachments,
        # TODO: BCC? Reply to?
    )
    email.send(fail_silently=False)


def process_inbound_email(data: MultiValueDict, files: MultiValueDict):
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
        for key, file in files.items():
            file = files[key]
            EmailAttachment.objects.create(
                email=email, file=file, content_type=file.content_type
            )
