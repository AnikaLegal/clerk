import ast

from auditlog.models import LogEntry
from django.contrib.contenttypes.models import ContentType
from task.models import Task, TaskEvent
from task.models.event import TaskEventType
from task.models.task import RequestTaskType


def handle_create_task_log_entry(log_entry: LogEntry):
    assert log_entry.action == LogEntry.Action.CREATE
    assert log_entry.content_type == ContentType.objects.get_for_model(Task)

    actor = log_entry.actor
    changes = log_entry.changes_dict
    task_id = log_entry.object_id
    timestamp = log_entry.timestamp

    serialized_data_fields = log_entry.serialized_data.get("fields")
    task_type = serialized_data_fields.get("type")

    if task_type == RequestTaskType.APPROVAL:
        description_changes = changes.get("description")
        next_description = description_changes[1]

        requesting_task_changes = changes.get("requesting_task")
        next_requesting_task = requesting_task_changes[1]

        return TaskEvent.objects.create(
            type=TaskEventType.REQUEST,
            task_id=next_requesting_task,
            user=actor,
            data={
                "request_task_id": task_id,
            },
            note_html=next_description,
            created_at=timestamp,
        )


def handle_update_task_log_entry(log_entry: LogEntry):
    assert log_entry.action == LogEntry.Action.UPDATE
    assert log_entry.content_type == ContentType.objects.get_for_model(Task)

    serialized_data_fields = log_entry.serialized_data.get("fields")
    task_type = serialized_data_fields.get("type")

    if task_type == RequestTaskType.APPROVAL:
        _handle_approval_task_is_open_update(log_entry)
    else:
        _handle_task_assigned_to_update(log_entry)
        _handle_task_status_update(log_entry)


def _handle_approval_task_is_open_update(log_entry: LogEntry):
    is_open = log_entry.changes.get("is_open", None)
    if is_open:
        # NOTE: Changes are stored as strings instead of the literal python type
        # e.g. None is represented as "None" and True as "True". See
        # https://github.com/jazzband/django-auditlog/issues/675
        prev_is_open, next_is_open = [ast.literal_eval(x) for x in is_open]

        if prev_is_open and not next_is_open:
            is_approved = log_entry.additional_data.get("is_approved", None)
            comment = log_entry.additional_data.get("comment", None)

            serialized_data_fields = log_entry.serialized_data.get("fields")
            requesting_task_id = serialized_data_fields.get("requesting_task")

            for id in [log_entry.object_id, requesting_task_id]:
                # Task was closed.
                TaskEvent.objects.create(
                    type=TaskEventType.APPROVAL,
                    task_id=id,
                    user=log_entry.actor,
                    data={
                        "is_approved": is_approved,
                    },
                    note_html=comment,
                    created_at=log_entry.timestamp,
                )


def _handle_task_assigned_to_update(log_entry: LogEntry):
    assigned_to = log_entry.changes.get("assigned_to", None)
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
                type=TaskEventType.CANCELLED,
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
