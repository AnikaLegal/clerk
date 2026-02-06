import logging

from accounts import events
from accounts.models import CaseGroups, User
from core.models import Issue
from django.conf import settings
from django.contrib.auth.models import Group
from django.db.models import Q
from django.utils import timezone
from emails.service.send import send_email
from utils.sentry import sentry_task

from .service import (
    set_up_new_case,
    set_up_new_user,
)

logger = logging.getLogger(__name__)


def reset_ms_access(user):
    if not user.is_active:
        logger.info("Skipping as User<%s> is inactive", user.pk)
        return

    _invite_user_if_not_exists(user)

    fifteen_minutes_ago = timezone.now() - timezone.timedelta(minutes=15)
    is_account_creation_finished = user.ms_account_created_at and (
        user.ms_account_created_at < fifteen_minutes_ago
    )
    if not is_account_creation_finished:
        logger.info("Skipping as User<%s> account is not created or too new", user.pk)
        return

    for group in user.groups.all():
        logger.info("Sending event for User<%s> added to Group<%s>", user.pk, group.pk)
        events.user_added_to_group.send(
            sender=User,
            user=user,
            group=group,
        )

    # NOTE: Not sure why 2022 used below. Maybe that was when Sharepoint was
    # introduced?
    for issue in Issue.objects.filter(
        Q(paralegal=user) | Q(lawyer=user),
        is_sharepoint_set_up=True,
        created_at__year__gte=2022,
    ).all():
        logger.info("Sending event for User<%s> added to Case<%s>", user.pk, issue.pk)
        events.user_added_to_case.send(
            sender=User,
            user=user,
            issue=issue,
        )


@sentry_task
def set_up_new_case_task(issue_pk: str):
    logger.info("Setting up folder on Sharepoint for Issue<%s>", issue_pk)
    issue = Issue.objects.get(pk=issue_pk)
    set_up_new_case(issue)
    Issue.objects.filter(pk=issue_pk).update(is_sharepoint_set_up=True)
    logger.info("Finished setting up folder on Sharepoint for Issue<%s>", issue_pk)


@sentry_task
def set_up_new_user_task(user_pk: int):
    """
    Give new users MS account and E1 license
    """
    logger.info("Setting up MS account for new User<%s>", user_pk)
    user = User.objects.get(pk=user_pk)

    # Add user to paralegals group.
    paralegal_group = Group.objects.get(name=CaseGroups.PARALEGAL)
    user.groups.add(paralegal_group)

    _invite_user_if_not_exists(user)
    User.objects.filter(pk=user.pk).update(ms_account_created_at=timezone.now())
    logger.info("Finished setting up MS account for new User<%s>", user_pk)


INVITE_BODY_TEMPLATE = """
Hello {name},

You have been invited to join Anika's Clerk case management system.
You can log in at https://www.anikalegal.com/case/ using your Anika Gmail account.

You have also been granted a Microsoft Office 365 login so that you can access case documents:

- username: {email}
- password: {password}

You will need to change your Microsoft password when you first log in.
We recommend that you set up Bitwarden (https://bitwarden.com/) to store all your Anika passwords.
"""


def _invite_user_if_not_exists(user):
    # Send invite email
    password = set_up_new_user(user)
    if password:
        # New MS account has been created.
        logger.info("Sending invite email to new User<%s>", user.pk)
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
