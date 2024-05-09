import logging
from django.db.models import Q
from utils.sentry import sentry_task

from accounts.models import User
from core.models import Issue, IssueEvent
from core.models.issue_event import EventType
from task.models import TaskTrigger, Task
from task.models.trigger import TriggerTopic, TasksCaseRole
from task.models.task import TaskStatus

from .helpers import (
    is_user_removed,
    is_user_changed,
    is_user_assigned_to_issue,
    is_lawyer_acting_as_paralegal,
    get_open_tasks_by_user,
    get_triggers_by_issue_event,
)

logger = logging.getLogger(__name__)


@sentry_task
def handle_event(event_pk: int):
    event = IssueEvent.objects.get(pk=event_pk)
    maybe_update_tasks(event)
    maybe_create_tasks(event)


def maybe_update_tasks(event: IssueEvent):
    """
    Update task ownership/assignee if the case lawyer or paralegal changes or is
    removed.
    """
    if is_user_removed(event):
        issue = event.issue
        prev = event.prev_user

        tasks = get_open_tasks_by_user(issue, prev)
        for task in tasks:
            task.status = TaskStatus.NOT_DONE
            # TODO: add comment describing action.
            task.save()

    elif is_user_changed(event):
        issue = event.issue
        prev = event.prev_user
        next = event.next_user

        # Don't update the tasks for a user that is still active on the case
        # i.e. they are still set as the lawyer or paralegal. This handles the 
        # presumably rare edge case where the lawyer is acting as the paralegal
        # & then the paralegal is changed. We cannot determine which tasks
        # belong to their role as the lawyer & which to their role as paralegal
        # so we do nothing.
        if not is_user_assigned_to_issue(issue, prev):
            tasks = get_open_tasks_by_user(issue, prev)
            for task in tasks:
                task.owner = next
                task.assigned_to = next
                task.save()


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
