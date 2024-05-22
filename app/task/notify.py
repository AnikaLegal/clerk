import logging
from django.db.models import QuerySet
from django.db import transaction

from accounts.models import User
from task.models import Task
from slack.services import get_slack_user_by_email, send_slack_direct_message
from django.template.loader import render_to_string

logger = logging.getLogger(__name__)


@transaction.atomic
def notify_of_assignment(task_pks: list[int], force: bool = False) -> None:
    """
    Notify users of task assignment if the supplied tasks have pending
    notifications. If the "force" parameter is true we notify users of task
    assignment without checking for pending notification.
    """
    if not task_pks:
        logger.warning("No tasks provided")
        return

    try:  # TODO: Finer grained error handling?
        tasks = Task.objects.filter(pk__in=task_pks)
        for task in tasks.distinct("assigned_to").exclude(assigned_to_id__isnull=True):
            user = task.assigned_to
            tasks_by_user = tasks.select_for_update().filter(assigned_to_id=user.pk)
            if not force:
                tasks_by_user = tasks_by_user.filter(
                    is_notify_pending=True, is_system_update=False
                )
            if tasks_by_user.exists():
                notify_user_of_assignment(user, tasks_by_user)
    finally:
        tasks.update(is_notify_pending=False, is_system_update=False)


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
