import logging
from datetime import timedelta
import ast

from accounts.models import User
from auditlog.models import LogEntry
from core.models import Issue, IssueEvent
from core.models.issue_event import EventType
from django.db import transaction
from django.db.models import Q
from django.utils import timezone
from task.helpers import get_coordinators_user
from task.models import Task, TaskEvent, TaskGroup, TaskTrigger
from task.models.task import TaskStatus, RequestTaskType
from task.models.event import TaskEventType
from task.models.trigger import TasksCaseRole, TriggerTopic
from utils.sentry import sentry_task

from .helpers import (
    is_case_closed,
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
        elif is_case_closed(event):
            # We don't notify when tasks are cancelled.
            cancelled_tasks = maybe_cancel_tasks(event)
            logger.info("Cancelled task(s): %s", cancelled_tasks)

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


@sentry_task
def handle_task_log(log_entry_pk: int):
    log_entry = LogEntry.objects.get(pk=log_entry_pk)

    # NOTE: Changes are stored as strings instead of the literal python type
    # e.g. None is represented as "None" and True as "True". See
    # https://github.com/jazzband/django-auditlog/issues/675
    changes = log_entry.changes_dict
    action = log_entry.action
    user = log_entry.actor
    task_id = log_entry.object_id
    timestamp = log_entry.timestamp

    additional_data = log_entry.additional_data
    serialized_data = log_entry.serialized_data.get("fields")
    task_type = serialized_data.get("type")

    if action == LogEntry.Action.CREATE:
        if task_type == RequestTaskType.APPROVAL:
            _, description = changes.get("description")
            _, requesting_task_id = changes.get("requesting_task")

            return TaskEvent.objects.create(
                type=TaskEventType.REQUEST,
                task_id=requesting_task_id,
                user=user,
                data={
                    "request_task_id": task_id,
                },
                note_html=description,
                created_at=timestamp,
            )

    if action == LogEntry.Action.UPDATE:
        if task_type == RequestTaskType.APPROVAL:
            is_open = changes.get("is_open", None)
            if is_open:
                # Convert to literal python type, see above.
                prev_is_open, next_is_open = [ast.literal_eval(x) for x in is_open]

                # TODO:
                is_approved = additional_data.get("is_approved", None)
                comment = additional_data.get("comment", None)

                requesting_task_id = serialized_data.get("requesting_task")

                if prev_is_open and not next_is_open:
                    for id in [task_id, requesting_task_id]:
                        # Task was closed.
                        TaskEvent.objects.create(
                            type=TaskEventType.APPROVAL,
                            task_id=id,
                            user=user,
                            data={
                                "is_approved": is_approved,
                            },
                            note_html=comment,
                            created_at=timestamp,
                        )
                else:
                    # Task was reopened.
                    pass
        else:
            assigned_to = changes.get("assigned_to", None)
            if assigned_to:
                # Convert to literal python type, see above.
                prev_id, next_id = [ast.literal_eval(x) for x in assigned_to]

                if prev_id and not next_id:
                    TaskEvent.objects.create(
                        type=TaskEventType.SUSPEND,
                        task_id=task_id,
                        user=user,
                        data={
                            "prev_user_id": prev_id,
                        },
                        created_at=timestamp,
                    )
                elif not prev_id and next_id:
                    TaskEvent.objects.create(
                        type=TaskEventType.RESUME,
                        task_id=task_id,
                        user=user,
                        data={
                            "next_user_id": next_id,
                        },
                        created_at=timestamp,
                    )
                elif prev_id and next_id and prev_id != next_id:
                    TaskEvent.objects.create(
                        type=TaskEventType.REASSIGN,
                        task_id=task_id,
                        user=user,
                        data={
                            "prev_user_id": prev_id,
                            "next_user_id": next_id,
                        },
                        created_at=timestamp,
                    )

            status = changes.get("status", None)
            if status:
                prev_status, next_status = status
                is_case_closed = additional_data.get("is_case_closed", False)
                if is_case_closed:
                    TaskEvent.objects.create(
                        type=TaskEventType.CANCELLED,
                        task_id=task_id,
                        user=user,
                        created_at=timestamp,
                    )
                else:
                    comment = additional_data.get("comment", None)
                    TaskEvent.objects.create(
                        type=TaskEventType.STATUS_CHANGE,
                        task_id=task_id,
                        user=user,
                        data={
                            "prev_status": prev_status,
                            "next_status": next_status,
                        },
                        note_html=comment,
                        created_at=timestamp,
                    )


def maybe_suspend_tasks(event: IssueEvent) -> list[int]:
    """
    Suspend tasks assigned to the user being removed from the case.
    """
    assert is_user_removed(event)

    event_type = event.event_type
    issue = event.issue
    prev_user = event.prev_user

    # If the removed user is no longer assigned to the case then we also need to
    # suspend their tasks that were created manually (i.e. don't have an
    # assignee_role value)
    q_filter = Q(assignee_role=event_type)
    if event.prev_user not in [issue.paralegal, issue.lawyer]:
        q_filter |= Q(assignee_role__isnull=True)

    tasks = Task.objects.filter(
        q_filter,
        issue=issue,
        is_open=True,
        assigned_to=prev_user,
    )
    for task in tasks:
        task.assigned_to = None
        # Set the assignee role so we know who to assign the task to if it is
        # resumed.
        task.assignee_role = event_type
        task.is_system_update = True
        task.save()

    return [task.pk for task in tasks]


def maybe_reassign_tasks(event: IssueEvent) -> list[int]:
    """
    Update task assignee if the case lawyer or paralegal changes.
    """
    assert is_user_changed(event)

    event_type = event.event_type
    issue = event.issue
    prev_user = event.prev_user
    next_user = event.next_user

    # If the previous user is no longer assigned to the case then we also need
    # to reassign their tasks that were created manually (i.e. don't have an
    # assignee_role value)
    q_filter = Q(assignee_role=event_type)
    if event.prev_user not in [issue.paralegal, issue.lawyer]:
        q_filter |= Q(assignee_role__isnull=True)

    tasks = Task.objects.filter(
        q_filter, issue=issue, is_open=True, assigned_to=prev_user
    )
    for task in tasks:
        task.assigned_to = next_user
        task.is_system_update = True
        task.save()

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

    return [task.pk for task in tasks]


def maybe_cancel_tasks(event: IssueEvent) -> list[int]:
    """
    Cancel all related tasks.
    """
    assert is_case_closed(event)

    issue = event.issue
    tasks = Task.objects.filter(issue=issue, is_open=True)
    for task in tasks:
        task.set_log_data("is_case_closed", True)
        task.status = TaskStatus.NOT_DONE
        try:
            task.save()
        finally:
            task.clear_log_data()

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
        # previously used stage that was set to activate a task trigger. If we
        # find one then don't use that template to create a task.
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
        return get_coordinators_user()
    return None
