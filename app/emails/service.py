import logging

from django.conf import settings
from django.core.mail import EmailMultiAlternatives


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
