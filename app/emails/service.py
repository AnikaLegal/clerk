import json
import logging
from typing import Optional
from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.utils.datastructures import MultiValueDict

from core.models import Issue
from .models import Email, EmailAttachment, EmailState


logger = logging.getLogger(__name__)


"""
from emails.service import send_email, build_sender_address
user = User.objects.last()
issue = Issue.objects.last()
from_email = build_sender_address(user, issue)
send_email(from_email, "mattdsegal@gmail.com", "Welcome Matt", "This is the body")
"""


def send_all_emails():
    """
    Sends all emails that are ready to be sent.
    FIXME: TEST MEEE
    """
    pass


def ingest_all_emails():
    """
    Ingests all received emails and attempts to associate them with related issues.
    FIXME: TEST MEEE
    """
    pass


def build_clerk_address(issue, user):
    """
    FIXME: TEST MEEE.
    """
    issue_prefix = str(issue.id).split("-")[0]
    full_name = user.get_full_name()
    email = f"case.{issue_prefix}@{settings.EMAIL_DOMAIN}"
    return f"{full_name} <{email}>"


def parse_clerk_address(email_addr: str) -> Optional[Issue]:
    """
    FIXME: TEST MEEE.
    """
    try:
        user, domain = email_addr.split("@")
        assert domain == settings.EMAIL_DOMAIN, f"Incorrect domain {domain}"
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
):
    """
    Send an email.
    FIXME: TEST MEEE.
    TODO: Add attachments
    """
    logger.info("Sending email to %s from %s", to_addr, from_addr)
    email = EmailMultiAlternatives(
        subject=subject,
        body=body,
        from_email=from_addr,
        to=[to_addr],
    )
    email.send(fail_silently=False)


def process_inbound_email(data: MultiValueDict, files: MultiValueDict):
    """
    Parse an inbound email from SendGrid and save as an Email.
    """
    envelope = json.loads(data["envelope"])
    email_data = {
        "from_addr": envelope["from"],
        "to_addrs": data["to"],
        "cc_addrs": data.get("cc", ""),
        "subject": data["subject"],
        "state": EmailState.RECEIVED,
        "text": data["text"].replace("\r\n", "\n"),
        "html": data.get("html", ""),
    }
    email = Email.objects.create(**email_data)
    # FIXME: Mangles non-ASCII UTF-8 text.
    for key, file in files.items():
        file = files[key]
        EmailAttachment.objects.create(
            email=email, file=file, content_type=file.content_type
        )
