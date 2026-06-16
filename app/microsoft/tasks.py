import logging
import time

from accounts import events
from accounts.models import User
from core.models import Issue
from django.db.models import Q
from django.utils import timezone
from microsoft.service import add_office_licence
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

    set_up_new_user(user)

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
def assign_user_licence(user_pk: int):
    # Try multiple times with some delay in between to allow for eventual
    # consistency in Microsoft Graph after account creation.
    user = User.objects.get(pk=user_pk)
    for _ in range(10):
        result = add_office_licence(user)
        if result:
            logger.info("Successfully assigned Microsoft licence to User<%s>", user.pk)
            return
        else:
            logger.warning(
                "Failed to assign Microsoft licence to User<%s> on attempt, retrying...",
                user.pk,
            )
        time.sleep(6)

    logger.error(
        "Failed to assign Microsoft licence to User<%s> after multiple attempts",
        user.pk,
    )
