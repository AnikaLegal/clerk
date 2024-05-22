import logging
from django.db.models import QuerySet
from django.db import transaction

from accounts.models import User
from task.models import Task
from slack.services import get_slack_user_by_email, send_slack_direct_message
from django.template.loader import render_to_string

logger = logging.getLogger(__name__)


@transaction.atomic
def notify_of_assignment(tasks: QuerySet[Task]) -> None:
    assert tasks.exists()
    logger.info("Notifying assignment of %s task(s)", tasks.count())

    for task in tasks.distinct("assigned_to").exclude(assigned_to_id__isnull=True):
        user = task.assigned_to
        tasks_by_user = tasks.select_for_update().filter(assigned_to_id=user.pk)
        notify_user_of_assignment(user, tasks_by_user)


def notify_user_of_assignment(user: User, tasks: QuerySet[Task]) -> None:
    assert tasks.exists()
    logger.info("Notifying User<%s> assignment of %s tasks", user.pk, tasks.count())

    # TODO: template needs work.
    context = {"tasks": list(tasks.values())}
    text = render_to_string("task/tasks_assigned.md", context)
    notify_user(user, text)


def notify_user(user: User, text: str) -> None:
    email = user.email
    slack_user = get_slack_user_by_email(email)
    if slack_user:
        send_slack_direct_message(text, slack_user["id"])
