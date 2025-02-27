import ast

from auditlog.models import LogEntry
from django.contrib.contenttypes.models import ContentType
from task.models import Task, TaskEvent
from task.models.event import TaskEventType
from task.models.task import RequestTaskType


def handle_create_task_log_entry(log_entry: LogEntry):
    assert log_entry.action == LogEntry.Action.CREATE
    assert log_entry.content_type == ContentType.objects.get_for_model(Task)

    type_changes = log_entry.changes.get("type")
    next_type = type_changes[1]

    if next_type == RequestTaskType.APPROVAL:
        _handle_approval_task_creation(log_entry)


def handle_update_task_log_entry(log_entry: LogEntry):
    assert log_entry.action == LogEntry.Action.UPDATE
    assert log_entry.content_type == ContentType.objects.get_for_model(Task)

    _handle_task_is_approval_pending_update(log_entry)
    _handle_task_assigned_to_update(log_entry)
    _handle_task_status_update(log_entry)


def _handle_approval_task_creation(log_entry: LogEntry):
    description_changes = log_entry.changes.get("description")
    next_description = description_changes[1]

    requesting_task_changes = log_entry.changes.get("requesting_task")
    next_requesting_task = requesting_task_changes[1]

    return TaskEvent.objects.create(
        type=TaskEventType.APPROVAL_REQUEST,
        task_id=next_requesting_task,
        user=log_entry.actor,
        data={
            "request_task_id": log_entry.object_id,
        },
        note_html=next_description,
        created_at=log_entry.timestamp,
    )


def _handle_task_is_approval_pending_update(log_entry: LogEntry):
    if not log_entry.changes:
        return

    is_approval_pending: list | None = log_entry.changes.get(
        "is_approval_pending", None
    )
    if is_approval_pending:
        # NOTE: Changes are stored as strings instead of the literal python type
        # e.g. None is represented as "None" and True as "True". See
        # https://github.com/jazzband/django-auditlog/issues/675
        prev_is_approval_pending, next_is_approval_pending = [
            ast.literal_eval(x) for x in is_approval_pending
        ]
        if prev_is_approval_pending and not next_is_approval_pending:
            serialized_data_fields = log_entry.serialized_data.get("fields")
            is_approved = serialized_data_fields.get("is_approved")

            additional_data = log_entry.additional_data
            comment = additional_data.get("comment", None)

            event = TaskEvent.objects.create(
                type=TaskEventType.APPROVAL_RESPONSE,
                task_id=log_entry.object_id,
                user=log_entry.actor,
                data={
                    "is_approved": is_approved,
                },
                note_html=comment,
                created_at=log_entry.timestamp,
            )

            # Duplicate event for the request task.
            request_task_id = additional_data.get("request_task_id", None)
            if request_task_id:
                event.pk = None
                event.task_id = request_task_id
                event.save()


def _handle_task_assigned_to_update(log_entry: LogEntry):
    if not log_entry.changes:
        return

    assigned_to: list | None = log_entry.changes.get("assigned_to", None)
    if assigned_to:
        # Convert to literal python type, see above.
        prev_id, next_id = [ast.literal_eval(x) for x in assigned_to]

        if prev_id and not next_id:
            TaskEvent.objects.create(
                type=TaskEventType.SUSPEND,
                task_id=log_entry.object_id,
                user=log_entry.actor,
                data={
                    "prev_user_id": prev_id,
                },
                created_at=log_entry.timestamp,
            )
        elif not prev_id and next_id:
            TaskEvent.objects.create(
                type=TaskEventType.RESUME,
                task_id=log_entry.object_id,
                user=log_entry.actor,
                data={
                    "next_user_id": next_id,
                },
                created_at=log_entry.timestamp,
            )
        elif prev_id and next_id and prev_id != next_id:
            TaskEvent.objects.create(
                type=TaskEventType.REASSIGN,
                task_id=log_entry.object_id,
                user=log_entry.actor,
                data={
                    "prev_user_id": prev_id,
                    "next_user_id": next_id,
                },
                created_at=log_entry.timestamp,
            )


def _handle_task_status_update(log_entry: LogEntry):
    status = log_entry.changes.get("status", None)
    if status:
        prev_status, next_status = status

        is_case_closed = log_entry.additional_data.get("is_case_closed", False)
        if is_case_closed:
            TaskEvent.objects.create(
                type=TaskEventType.CANCEL,
                task_id=log_entry.object_id,
                user=log_entry.actor,
                created_at=log_entry.timestamp,
            )
        else:
            comment = log_entry.additional_data.get("comment", None)
            TaskEvent.objects.create(
                type=TaskEventType.STATUS_CHANGE,
                task_id=log_entry.object_id,
                user=log_entry.actor,
                data={
                    "prev_status": prev_status,
                    "next_status": next_status,
                },
                note_html=comment,
                created_at=log_entry.timestamp,
            )
