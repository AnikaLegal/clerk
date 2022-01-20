import logging

from django.conf import settings

from utils.sentry import WithSentryCapture
from core.models import Issue
from accounts.models import User, CaseGroups
from django.contrib.auth.models import Group
from emails.service.send import send_email
from .service import set_up_new_case, set_up_new_user


logger = logging.getLogger(__name__)


def _set_up_new_case_task(issue_pk: str):
    logger.info("Setting up folder on Sharepoint for Issue<%s>", issue_pk)
    issue = Issue.objects.get(pk=issue_pk)
    set_up_new_case(issue)
    Issue.objects.filter(pk=issue_pk).update(is_sharepoint_set_up=True)
    logger.info("Finished setting up folder on Sharepoint for Issue<%s>", issue_pk)


set_up_new_case_task = WithSentryCapture(_set_up_new_case_task)


INVITE_BODY_TEMPLATE = """
Hello {name},

You have been invited to join Anika's Clerk case management system.
You can log in at https://clerk.anikalegal.com/case/ using your Anika Gmail account.

You have also been granted a Microsoft Office 365 login so that you can access case documents:

- username: {email}
- password: {password}

You will need to change your Microsoft password when you first log in.
We recommend that you set up Bitwarden (https://bitwarden.com/) to store all your Anika passwords.
"""


def _set_up_new_user_task(user_pk: int):
    """
    Give new users MS account and E1 license
    """
    logger.info("Setting up MS account for new User<%s>", user_pk)
    user = User.objects.get(pk=user_pk)

    # Add user to paralegals group.
    paralegal_group = Group.objects.get(name=CaseGroups.PARALEGAL)
    user.groups.add(paralegal_group)

    # Send invite email
    password = set_up_new_user(user)
    if password:
        # New MS account has been created.
        logger.info("Sending invite email to new User<%s>", user_pk)
        body = INVITE_BODY_TEMPLATE.strip().format(
            name=user.get_full_name(),
            email=user.email,
            password=password,
        )
        send_email(
            from_addr=f"noreply@{settings.EMAIL_DOMAIN}",
            to_addr=user.email,
            cc_addrs=[],
            subject="You have been invited to join Anika's Clerk case management system.",
            body=body,
        )

    logger.info("Finished setting up MS account for new User<%s>", user_pk)


set_up_new_user_task = WithSentryCapture(_set_up_new_user_task)
