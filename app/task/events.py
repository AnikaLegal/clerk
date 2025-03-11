import ast

from auditlog.models import LogEntry
from django.contrib.contenttypes.models import ContentType
from task.models import Task, TaskEvent, TaskRequest
from task.models.request import TaskRequestType, TaskRequestStatus
from task.models.event import TaskEventType


def handle_update_task_log_entry(log_entry: LogEntry):
    assert log_entry.action == LogEntry.Action.UPDATE
    assert log_entry.content_type == ContentType.objects.get_for_model(Task)

    _handle_task_assigned_to_update(log_entry)
    _handle_task_status_update(log_entry)


def handle_create_task_request_log_entry(log_entry: LogEntry):
    assert log_entry.action == LogEntry.Action.CREATE
    assert log_entry.content_type == ContentType.objects.get_for_model(TaskRequest)

    _handle_task_request_approval_create(log_entry)


def handle_update_task_request_log_entry(log_entry: LogEntry):
    assert log_entry.action == LogEntry.Action.UPDATE
    assert log_entry.content_type == ContentType.objects.get_for_model(TaskRequest)

    _handle_task_request_approval_status_update(log_entry)


def _handle_task_assigned_to_update(log_entry: LogEntry):
    if not log_entry.changes:
        return

    assigned_to: list | None = log_entry.changes.get("assigned_to", None)
    if assigned_to:
        # NOTE: django-auditlog stores changes as strings. See
        # https://github.com/jazzband/django-auditlog/issues/675. This is a bit
        # of an annoyance to work with so we convert to literal python types.
        prev_id, next_id = [ast.literal_eval(x) for x in assigned_to]

        if prev_id and not next_id:
            TaskEvent.objects.create(
                type=TaskEventType.SUSPENDED,
                task_id=log_entry.object_id,
                user=log_entry.actor,
                data={
                    "prev_user_id": prev_id,
                },
                created_at=log_entry.timestamp,
            )
        elif not prev_id and next_id:
            TaskEvent.objects.create(
                type=TaskEventType.RESUMED,
                task_id=log_entry.object_id,
                user=log_entry.actor,
                data={
                    "next_user_id": next_id,
                },
                created_at=log_entry.timestamp,
            )
        elif prev_id and next_id and prev_id != next_id:
            TaskEvent.objects.create(
                type=TaskEventType.REASSIGNED,
                task_id=log_entry.object_id,
                user=log_entry.actor,
                data={
                    "prev_user_id": prev_id,
                    "next_user_id": next_id,
                },
                created_at=log_entry.timestamp,
            )


def _handle_task_status_update(log_entry: LogEntry):
    if not log_entry.changes:
        return

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
                note_html=comment if comment else "",
                created_at=log_entry.timestamp,
            )


def _handle_task_request_approval_status_update(log_entry: LogEntry):
    if not log_entry.serialized_data:
        return

    data = log_entry.serialized_data.get("fields")
    type = data.get("type")
    status = data.get("status")

    if type == TaskRequestType.APPROVAL and status == TaskRequestStatus.DONE:
        is_approved = data.get("is_approved")
        comment = data.get("to_comment")

        event = TaskEvent.objects.create(
            type=TaskEventType.REQUEST_ACCEPTED
            if is_approved
            else TaskEventType.REQUEST_DECLINED,
            task_id=data.get("to_task"),
            user=log_entry.actor,
            note_html=comment if comment else "",
            created_at=log_entry.timestamp,
        )

        # Clone the event and set the ownership to the requesting ("from") task.
        event.pk = None
        event.task_id = data.get("from_task")
        event.save()


def _handle_task_request_approval_create(log_entry: LogEntry):
    if not log_entry.serialized_data:
        return

    data = log_entry.serialized_data.get("fields")
    type = data.get("type")
    status = data.get("status")

    if type == TaskRequestType.APPROVAL and status == TaskRequestStatus.PENDING:
        comment = data.get("from_comment")

        TaskEvent.objects.create(
            type=TaskEventType.APPROVAL_REQUEST,
            task_id=data.get("from_task"),
            user=log_entry.actor,
            note_html=comment if comment else "",
            data={
                "to_task_id": data.get("to_task"),
            },
            created_at=log_entry.timestamp,
        )
