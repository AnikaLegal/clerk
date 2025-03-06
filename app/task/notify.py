import logging

from accounts.models import User
from core.models import Issue
from django.conf import settings
from django.db.models import QuerySet
from django.template.loader import render_to_string
from slack.services import (
    get_slack_user_by_email,
    send_slack_direct_message,
    send_slack_message,
)
from task.helpers import get_coordinators_user
from task.models import Task

logger = logging.getLogger(__name__)


def notify_of_task_assignment(task_pks: list[int]) -> None:
    assert task_pks
    tasks = Task.objects.filter(pk__in=task_pks)
    assert tasks.exists()
    logger.info("Notifying assignment of task(s): %s", task_pks)

    for task in tasks.distinct("assigned_to", "issue"):
        if task.assigned_to:
            tasks_by_user_and_issue = tasks.filter(
                assigned_to=task.assigned_to, issue=task.issue
            )
            notify_user_of_task_assignment(
                task.assigned_to, task.issue, tasks_by_user_and_issue
            )


def notify_user_of_task_assignment(
    user: User, issue: Issue, tasks: QuerySet[Task]
) -> None:
    assert tasks.exists()
    logger.info(
        "Notifying User<%s> assignment of task(s) related to Issue<%s>: %s",
        user.pk,
        issue.pk,
        [t.pk for t in tasks],
    )
    text = get_assignment_notify_text(issue, tasks)
    notify_user(user, text)


def get_assignment_notify_text(issue, tasks: QuerySet[Task]) -> str:
    assert tasks.exists()
    context = {"issue": issue, "tasks": tasks, "base_url": settings.CLERK_BASE_URL}
    return render_to_string("task/tasks_assigned.md", context)


def notify_user(user: User, text: str) -> None:
    coordinators = get_coordinators_user()
    if user == coordinators:
        send_slack_message(settings.SLACK_MESSAGE.COORDINATOR_TASK, text)
    else:
        slack_user = get_slack_user_by_email(user.email)
        if slack_user:
            send_slack_direct_message(text, slack_user["id"])
