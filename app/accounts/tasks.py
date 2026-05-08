import logging

from django.conf import settings
from emails.service.send import send_email
from utils.sentry import sentry_task

from accounts.models import User

logger = logging.getLogger(__name__)

WELCOME_BODY_TEMPLATE = """
Hello {name},

You have been invited to join Anika's Clerk case management system.
You can log in at https://anikalegal.org.au/clerk/cases/ using your Anika Gmail account.

You have also been granted a Microsoft Office 365 login so that you can access case documents:

- username: {email}
- password: {password}

You will need to change your Microsoft password when you first log in.
We recommend that you set up Bitwarden (https://bitwarden.com/) to store all your Anika passwords.
"""


@sentry_task
def welcome_user_task(user_pk: int):
    user: User = User.objects.get(pk=user_pk)
    logger.info("Sending welcome email to new User<%s>", user.pk)
    body = WELCOME_BODY_TEMPLATE.strip().format(
        name=user.get_full_name(),
        email=user.email,
        password=user.ms_account_initial_password,
    )
    send_email(
        from_addr=f"noreply@{settings.EMAIL_DOMAIN}",
        to_addr=user.email,
        cc_addrs=[],
        subject="You have been invited to join Anika's Clerk case management system.",
        body=body,
    )
    User.objects.filter(pk=user.pk).update(ms_account_initial_password=None)
