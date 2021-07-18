import logging

from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.utils.datastructures import MultiValueDict

from .models import Email, EmailAttachment

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
    import pdb

    pdb.set_trace()
    # Email
    # data, files
