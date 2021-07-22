import json
import logging

from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.utils.datastructures import MultiValueDict

from .models import Email, EmailAttachment, EmailState

logger = logging.getLogger(__name__)


"""
from emails.service import send_email
send_email("guy", "mattdsegal@gmail.com", "Welcome Matt", "This is the body")
"""


def send_email(
    from_username: str,
    to_addr: str,
    subject: str,
    body: str,
):
    """
    Send an email.
    """
    from_addr = f"{from_username}@{settings.EMAIL_DOMAIN}"
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
        "to_addr": envelope["to"][0],
        "to_addrs": data["to"],
        "cc_addrs": data.get("cc", ""),
        "subject": data["subject"],
        "state": EmailState.RECEIVED,
        "text": data["text"].replace("\r\n", "\n"),
        "html": data.get("html", ""),
    }
    email = Email.objects.create(**email_data)
    # FIXME: Mangles UTF-8 text.
    for key, file in files.items():
        file = files[key]
        EmailAttachment.objects.create(
            email=email, file=file, content_type=file.content_type
        )
