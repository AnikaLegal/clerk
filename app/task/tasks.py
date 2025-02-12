import logging
from datetime import timedelta

from accounts.models import User
from core.models import Issue, IssueEvent
from core.models.issue_event import EventType
from django.db import transaction
from django.db.models import Q
from django.utils import timezone
from task.helpers import get_coordinators_user
from task.models import Task, TaskEvent, TaskGroup, TaskTrigger
from task.models.trigger import TasksCaseRole, TriggerTopic
from utils.sentry import sentry_task

from .helpers import (
    is_lawyer_acting_as_paralegal,
    is_user_added,
    is_user_changed,
    is_user_removed,
)
from .notify import notify_of_assignment

logger = logging.getLogger(__name__)


@sentry_task
@transaction.atomic
def handle_event_save(event_pk: int):
    event = IssueEvent.objects.get(pk=event_pk)
    logger.info(
        'Handling "%s" IssueEvent<%s> on Issue<%s>',
        event.event_type,
        event.pk,
        event.issue_id,
    )
    notify_tasks: set[int] = set()

    if is_user_removed(event):
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
        try:
            notify_of_assignment(list(notify_tasks))
        finally:
            Task.objects.filter(pk__in=notify_tasks).update(
                is_notify_pending=False, is_system_update=False
            )


@sentry_task
def handle_task_save(task_pk: int):
    task = Task.objects.get(pk=task_pk)
    try:
        if task and task.is_notify_pending and not task.is_system_update:
            notify_of_assignment([task.pk])
    finally:
        if task and (task.is_notify_pending or task.is_system_update):
            task.is_notify_pending = False
            task.is_system_update = False
            task.save()


def maybe_suspend_tasks(event: IssueEvent) -> list[int]:
    """
    Suspend tasks assigned to the user being removed from the case.
    """
    assert is_user_removed(event)

    issue = event.issue
    prev_user = event.prev_user

    tasks = Task.objects.filter(issue=issue, is_open=True, assigned_to=prev_user)
    for task in tasks:
        task.assigned_to = None
        task.is_system_update = True
        task.save()

        TaskEvent.create_suspend(task=task, prev_user=prev_user)

    return [task.pk for task in tasks]


def maybe_reassign_tasks(event: IssueEvent) -> list[int]:
    """
    Update task assignee if the case lawyer or paralegal changes.
    """
    assert is_user_changed(event)

    issue = event.issue
    prev_user = event.prev_user
    next_user = event.next_user

    tasks = Task.objects.filter(
        issue=issue, is_open=True, assigned_to=prev_user, assignee_role=event.event_type
    )
    for task in tasks:
        task.assigned_to = next_user
        task.is_system_update = True
        task.save()

        TaskEvent.create_reassign(task=task, prev_user=prev_user, next_user=next_user)

    return [task.pk for task in tasks]


def maybe_resume_tasks(event: IssueEvent) -> list[int]:
    """
    Resume tasks that were previously suspended when a user was removed from the
    case.
    """
    assert is_user_added(event)

    issue = event.issue
    next_user = event.next_user

    tasks = Task.objects.filter(
        issue=issue, is_suspended=True, assignee_role=event.event_type
    )
    for task in tasks:
        task.assigned_to = next_user
        task.is_system_update = True
        task.save()

        TaskEvent.create_resume(task=task, next_user=next_user)

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
    task_pks = []
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

        # Look for existing tasks related to the same issue, assigned to the
        # same user and created using the same template. This could happen if
        # the trigger was activated twice e.g. the case stage was set back to a
        # previously used stage that was set to activate a task trigger.
        templates = []
        for template in trigger.templates.all():
            query = Q(issue=event.issue, template=template, assigned_to=user)
            if not Task.objects.filter(query).exists():
                templates.append(template)

        # Create the tasks based on the templates.
        if templates:
            now = timezone.now()
            group = TaskGroup.objects.create(name=trigger.name)

            for template in templates:
                due_at = None
                if template.due_in:
                    due_at = (now + timedelta(days=template.due_in)).date()

                task = Task.objects.create(
                    issue=event.issue,
                    template=template,
                    group=group,
                    group_order=template._order,
                    type=template.type,
                    name=template.name,
                    description=template.description,
                    is_urgent=template.is_urgent,
                    is_approval_required=template.is_approval_required,
                    due_at=due_at,
                    assigned_to=user,
                    assignee_role=role,
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
        user = get_coordinators_user()
        return user
    return None
