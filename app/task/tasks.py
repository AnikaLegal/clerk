import logging
from utils.sentry import sentry_task
from django.db.models import Q
from django.db import transaction

from accounts.models import User
from core.models import Issue, IssueEvent
from core.models.issue_event import EventType
from task.models import Task, TaskTrigger
from task.models.trigger import TasksCaseRole, TriggerTopic

from .helpers import (
    is_user_added,
    is_user_changed,
    is_user_removed,
    is_user_assigned_to_issue,
    is_lawyer_acting_as_paralegal,
)
from .notify import notify_of_assignment

logger = logging.getLogger(__name__)


@sentry_task
@transaction.atomic
def handle_event(event_pk: int):
    event = IssueEvent.objects.get(pk=event_pk)
    logger.info(
        'Handling "%s" IssueEvent<%s> on Issue<%s>',
        event.event_type,
        event.pk,
        event.issue_id,
    )
    notify_tasks: set[int] = set()

    if is_user_removed(event):
        reverted_tasks = maybe_revert_tasks(event)
        logger.info("Reverted task(s): %s", reverted_tasks)
        notify_tasks.update(reverted_tasks)

        # We don't notify when tasks are suspended.
        suspended_tasks = maybe_suspend_tasks(event)
        logger.info("Suspended task(s): %s", suspended_tasks)

    elif is_user_changed(event):
        reassigned_tasks = maybe_reassign_tasks(event)
        logger.info("Reassigned task(s): %s", reassigned_tasks)
        notify_tasks.update(reassigned_tasks)
    else:
        if is_user_added(event):
            resumed_tasks = maybe_resume_tasks(event)
            logger.info("Resumed task(s): %s", resumed_tasks)
            notify_tasks.update(resumed_tasks)

        created_tasks = maybe_create_tasks(event)
        logger.info("Created task(s): %s", created_tasks)
        notify_tasks.update(created_tasks)

    if notify_tasks:
        tasks = Task.objects.filter(pk__in=notify_tasks)
        try:
            notify_of_assignment(tasks)
        finally:
            tasks.update(is_notify_pending=False, is_system_update=False)


@sentry_task
def handle_task(task_pk: int):
    # This is a somewhat unusual way of getting & using a single task. We do it
    # this way because it is convenient and allows us to use a single notify
    # method for one or more tasks.
    tasks = Task.objects.filter(pk=task_pk)
    try:
        task = tasks.first()
        if task.is_notify_pending and not task.is_system_update:
            notify_of_assignment(tasks)
    finally:
        if task.is_notify_pending or task.is_system_update:
            tasks.update(is_notify_pending=False, is_system_update=False)


@transaction.atomic
def maybe_revert_tasks(event: IssueEvent) -> list[int]:
    """
    Revert tasks assigned to but not owned by the user being removed from the
    case back to their owner.
    """
    assert is_user_removed(event)

    issue = event.issue
    prev_user = event.prev_user

    tasks = (
        Task.objects.select_for_update()
        .filter(issue=issue, is_open=True)
        .filter(Q(assigned_to=prev_user) & ~Q(owner=prev_user))
    )
    for task in tasks:
        task.assigned_to = task.owner
        task.is_system_update = True
        task.save()

        text = f"This task was reassigned back to {task.owner} because {prev_user} was removed from the case."
        task.add_comment(text)

    return [task.pk for task in tasks]


@transaction.atomic
def maybe_suspend_tasks(event: IssueEvent) -> list[int]:
    """
    Suspend tasks owned by the user being removed from the case.
    """
    assert is_user_removed(event)

    issue = event.issue
    prev_user = event.prev_user

    tasks = Task.objects.select_for_update().filter(
        issue=issue, is_open=True, owner=prev_user
    )
    for task in tasks:
        task.prev_owner_role = event.event_type
        task.owner = None
        task.assigned_to = None
        task.is_system_update = True
        task.save()

        text = f"This task was suspended because {prev_user} was removed from the case."
        task.add_comment(text)

    return [task.pk for task in tasks]


@transaction.atomic
def maybe_reassign_tasks(event: IssueEvent) -> list[int]:
    """
    Update task ownership/assignee if the case lawyer or paralegal changes.
    """
    assert is_user_changed(event)

    issue = event.issue
    prev_user = event.prev_user
    next_user = event.next_user

    # Don't update the tasks for a user that is still active on the case i.e.
    # they are still set as the lawyer or paralegal. This handles the presumably
    # rare edge case where the lawyer is acting as the paralegal & then the
    # paralegal is changed. We cannot determine which tasks belong to their role
    # as the lawyer & which to their role as paralegal so we do nothing.
    if is_user_assigned_to_issue(issue, prev_user):
        logger.info(
            "Not reassigning tasks as User<%s> still assigned to another role on case",
            prev_user.pk,
        )
        return []

    tasks = (
        Task.objects.select_for_update()
        .filter(issue=issue, is_open=True)
        .filter(Q(owner=prev_user) | Q(assigned_to=prev_user))
    )
    for task in tasks:
        if task.owner == prev_user:
            task.owner = next_user
        if task.assigned_to == prev_user:
            task.assigned_to = next_user
        task.is_system_update = True
        task.save()

        text = f"This task was reassigned from {prev_user} to {next_user} because the case user was changed."
        task.add_comment(text)

    return [task.pk for task in tasks]


@transaction.atomic
def maybe_resume_tasks(event: IssueEvent) -> list[int]:
    """
    Resume tasks that were previously suspended when a user was removed from the
    case.
    """
    assert is_user_added(event)

    issue = event.issue
    next_user = event.next_user

    tasks = Task.objects.select_for_update().filter(
        issue=issue, is_suspended=True, prev_owner_role=event.event_type
    )
    for task in tasks:
        task.owner = next_user
        task.assigned_to = next_user
        task.prev_owner_role = None
        task.is_system_update = True
        task.save()

        text = f"This task was resumed because {next_user} was added to the case."
        task.add_comment(text)

    return [task.pk for task in tasks]


def maybe_create_tasks(event: IssueEvent) -> list[int]:
    """
    Look for task triggers matching the event details and create tasks based on
    the templates associated with the trigger.
    """

    # Don't create any tasks if a user has been removed from a case.
    if is_user_removed(event):
        return []

    # Look for triggers matching the event.
    triggers = TaskTrigger.objects.filter(event=event.event_type)
    triggers = triggers.filter(topic__in=[event.issue.topic, TriggerTopic.ANY])
    if event.event_type == EventType.STAGE:
        triggers = triggers.filter(event_stage=event.next_stage)
    logger.debug("triggers.query: %s", triggers.query)

    # Create tasks based on the templates associated with any triggers.
    for trigger in triggers:
        logger.info("IssueEvent<%s> activated TaskTrigger<%s>", event.pk, trigger.pk)
        role = trigger.tasks_assignment_role
        user = get_user_by_role(event.issue, role)

        # TODO: check that we should handle this.
        # Handle special case - don't create paralegal tasks when a lawyer is
        # acting as the paralegal.
        if role == TasksCaseRole.PARALEGAL and is_lawyer_acting_as_paralegal(
            event.issue
        ):
            logger.info("Not creating tasks as lawyer is acting as paralegal")
            break

        task_pks = []
        for template in trigger.templates.all():
            if not Task.objects.filter(
                issue=event.issue, template=template, owner=user
            ).exists():
                task = Task.objects.create(
                    issue=event.issue,
                    template=template,
                    type=template.type,
                    name=template.name,
                    description=template.description,
                    owner=user,
                    is_system_update=True,
                )
                task_pks.append(task.pk)

        return task_pks


def get_user_by_role(issue: Issue, role: TasksCaseRole) -> User | None:
    if role == TasksCaseRole.PARALEGAL:
        return issue.paralegal
    if role == TasksCaseRole.LAWYER:
        return issue.lawyer
    if role == TasksCaseRole.COORDINATOR:
        # TODO: move this elsewhere.
        return User.objects.get(email="coordinators@anikalegal.com")
    return None
