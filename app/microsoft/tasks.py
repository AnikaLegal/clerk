import logging

from django.conf import settings
from django.utils import timezone
from django.contrib.auth.models import Group

from utils.sentry import WithSentryCapture
from core.models import Issue
from accounts.models import User, CaseGroups
from emails.service.send import send_email
from .service import (
    set_up_new_case,
    set_up_new_user,
    add_user_to_case,
    set_up_coordinator,
)


logger = logging.getLogger(__name__)


def refresh_ms_permissions(user):
    """
    Ensure all users who should have MS accounts get those accounts with correct permissions.
    """
    logger.info(
        "Refreshing MS account creation for User<%s:%s>",
        user.pk,
        user.get_full_name(),
    )
    _invite_user_if_not_exists(user)

    fifteen_minutes_ago = timezone.now() - timezone.timedelta(minutes=15)
    is_ms_account_set_up = user.ms_account_created_at and (
        user.ms_account_created_at < fifteen_minutes_ago
    )
    if not is_ms_account_set_up:
        logger.info(
            "Halting MS permission refresh for User<%s:%s> - account too new.",
            user.pk,
            user.get_full_name(),
        )
        return

    is_coordinator_or_better = (
        user.is_superuser
        or user.groups.filter(
            name__in=[CaseGroups.COORDINATOR, CaseGroups.ADMIN]
        ).exists()
    )
    is_paralegal = user.groups.filter(name=CaseGroups.PARALEGAL).exists()
    if is_coordinator_or_better:
        set_up_coordinator(user)
    elif is_paralegal:
        sharepoint_issues = (
            user.issue_set.select_related("paralegal")
            .filter(is_sharepoint_set_up=True, created_at__year__gte=2022)
            .all()
        )
        for issue in sharepoint_issues:
            logger.info(
                "Refreshing Sharepoint access for User<%s:%s> + Issue<%s>",
                issue.paralegal.pk,
                issue.paralegal.get_full_name(),
                issue.pk,
            )
            add_user_to_case(issue.paralegal, issue)


def _set_up_new_case_task(issue_pk: str):
    logger.info("Setting up folder on Sharepoint for Issue<%s>", issue_pk)
    issue = Issue.objects.get(pk=issue_pk)
    set_up_new_case(issue)
    Issue.objects.filter(pk=issue_pk).update(is_sharepoint_set_up=True)
    logger.info("Finished setting up folder on Sharepoint for Issue<%s>", issue_pk)


set_up_new_case_task = WithSentryCapture(_set_up_new_case_task)


def _set_up_new_user_task(user_pk: int):
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


set_up_new_user_task = WithSentryCapture(_set_up_new_user_task)


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
