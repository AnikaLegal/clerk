import logging
from utils.sentry import sentry_task

from accounts.models import User
from core.models import Issue, IssueEvent
from task.models import Task, TaskComment
from task.models.trigger import TasksCaseRole
from task.models.task import TaskStatus

from .helpers import (
    is_user_removed,
    is_user_changed,
    is_user_assigned_to_issue,
    is_lawyer_acting_as_paralegal,
    get_open_tasks_by_user,
    get_triggers_by_issue_event,
)

# TODO: add logging.
logger = logging.getLogger(__name__)


@sentry_task
def handle_event(event_pk: int):
    event = IssueEvent.objects.get(pk=event_pk)
    maybe_close_tasks(event)
    maybe_update_tasks(event)
    maybe_create_tasks(event)


def maybe_close_tasks(event: IssueEvent):
    """
    Close tasks if the case lawyer or paralegal is removed.
    """
    if is_user_removed(event):
        issue = event.issue
        prev_user = event.prev_user

        # TODO: handle task with different owner & assigned_to
        tasks = get_open_tasks_by_user(issue, prev_user)
        for task in tasks:
            task.status = TaskStatus.NOT_DONE
            task.save()

            text = f"This task was closed because the user {prev_user} was removed from the case."
            task.create_comment(text)


def maybe_update_tasks(event: IssueEvent):
    """
    Update task ownership/assignee if the case lawyer or paralegal changes.
    """
    if is_user_changed(event):
        issue = event.issue
        prev_user = event.prev_user
        next_user = event.next_user

        # Don't update the tasks for a user that is still active on the case
        # i.e. they are still set as the lawyer or paralegal. This handles the
        # presumably rare edge case where the lawyer is acting as the paralegal
        # & then the paralegal is changed. We cannot determine which tasks
        # belong to their role as the lawyer & which to their role as paralegal
        # so we do nothing.
        if not is_user_assigned_to_issue(issue, prev_user):
            tasks = get_open_tasks_by_user(issue, prev_user)
            for task in tasks:
                if task.owner == prev_user:
                    task.owner = next_user
                if task.assigned_to == prev_user:
                    task.assigned_to = next_user
                task.save()

                text = f"This task was reassigned from {prev_user} to {next_user} because the case user was changed."
                task.create_comment(text)


def maybe_create_tasks(event: IssueEvent):
    """
    Look for task triggers matching the event details and create tasks based on
    the templates associated with the trigger.
    """

    # Don't create any tasks if a user has been removed from a case.
    if is_user_removed(event):
        return

    for trigger in get_triggers_by_issue_event(event):
        role = trigger.tasks_assignment_role
        user = get_user_by_role(event.issue, role)

        # TODO: check that we should handle this.
        # Handle special case - don't create paralegal tasks when a lawyer is
        # acting as the paralegal.
        if role == TasksCaseRole.PARALEGAL and is_lawyer_acting_as_paralegal(
            event.issue
        ):
            break

        for template in trigger.templates.all():
            Task.objects.get_or_create(
                template=template,
                issue=event.issue,
                assigned_to=user,
                is_open=True,
                defaults={
                    "type": template.type,
                    "name": template.name,
                    "description": template.description,
                },
            )


def get_user_by_role(issue: Issue, role: TasksCaseRole) -> User | None:
    if role == TasksCaseRole.PARALEGAL:
        return issue.paralegal
    if role == TasksCaseRole.LAWYER:
        return issue.lawyer
    if role == TasksCaseRole.COORDINATOR:
        # TODO: move this elsewhere.
        return User.objects.get(email="coordinators@anikalegal.com")
    return None
