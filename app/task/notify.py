import logging
from django.db.models import QuerySet

from accounts.models import User
from task.models import Task
from slack.services import get_slack_user_by_email, send_slack_direct_message
from django.template.loader import render_to_string

logger = logging.getLogger(__name__)


def notify_of_assignment(tasks: QuerySet[Task]) -> None:
    assert tasks.exists()
    logger.info("Notifying assignment of task(s): %s", [t.pk for t in tasks])

    for task in tasks.distinct("assigned_to").exclude(assigned_to__isnull=True):
        user = task.assigned_to
        tasks_by_user = tasks.filter(assigned_to=user.pk)
        notify_user_of_assignment(user, tasks_by_user)


def notify_user_of_assignment(user: User, tasks: QuerySet[Task]) -> None:
    assert tasks.exists()
    logger.info(
        "Notifying User<%s> assignment of task(s): %s", user.pk, [t.pk for t in tasks]
    )
    # TODO: template needs work.
    context = {"tasks": list(tasks.values())}
    text = render_to_string("task/tasks_assigned.md", context)
    notify_user(user, text)


def notify_user(user: User, text: str) -> None:
    email = user.email
    slack_user = get_slack_user_by_email(email)
    if slack_user:
        send_slack_direct_message(text, slack_user["id"])
