import datetime
import re
from typing import Any, TypedDict

from auditlog.models import LogEntry
from auditlog.registry import auditlog
from django.core.exceptions import (
    FieldDoesNotExist,
)
from django.db.models import DateField, DateTimeField, Field, TimeField


class ActionInfo(TypedDict):
    model_name: str
    indefinite_article: str
    verb: str


class FieldInfo(TypedDict):
    verbose_name: str
    value: Any
    type: str
    is_changed: bool


def get_action_info(log_entry: LogEntry) -> ActionInfo:
    model_class = log_entry.content_type.model_class()

    verbose_model_name = model_class._meta.verbose_name
    indefinite_article = (
        "an" if verbose_model_name[0] in ("a", "e", "i", "o", "u") else "a"
    )
    verb = _get_verb(log_entry)

    return {
        "model_name": verbose_model_name,
        "indefinite_article": indefinite_article,
        "verb": verb,
    }


def get_field_info(log_entry: LogEntry) -> dict[str, FieldInfo]:
    field_values: dict[str, FieldInfo] = {}

    if log_entry.serialized_data:
        model_class = log_entry.content_type.model_class()
        ignore = _get_ignored_fields(model_class)

        changes = log_entry.changes_dict
        data = log_entry.serialized_data

        for field_name, value in data["fields"].items():  # type: ignore
            if _is_field_excluded(model_class, field_name) or field_name in ignore:
                continue

            verbose_name = field_name
            type = "unknown"

            field = _get_field(model_class, field_name)
            if field:
                verbose_name = field.verbose_name
                type = _get_field_type(field)
                value = _get_field_value(field, value)

            field_values[field_name] = {
                "verbose_name": verbose_name,
                "value": value,
                "type": type,
                "is_changed": field_name in changes,
            }

    return field_values


def _get_verb(log_entry: LogEntry) -> str:
    match log_entry.action:
        case LogEntry.Action.CREATE:
            return "added"
        case LogEntry.Action.DELETE:
            return "deleted"
        case LogEntry.Action.UPDATE:
            return "updated"
        case _:
            raise Exception(f"Unhandled event type: {log_entry.action}")


def _get_ignored_fields(model_class) -> set:
    try:
        return model_class.audit_event_ignore_fields()
    except AttributeError:
        pass
    return set()


def _is_field_excluded(model_class, field_name: str) -> bool:
    model = model_class._meta.model
    config = auditlog.get_model_fields(model) if auditlog.contains(model) else None
    return config is not None and field_name in config["exclude_fields"]


def _get_field(model_class, field_name: str) -> Field | None:
    try:
        return model_class._meta.get_field(field_name)
    except FieldDoesNotExist:
        pass
    return None


def _get_field_type(field: Field):
    try:
        type = field.get_internal_type()
        type = re.sub(r"(?<!^)(?=[A-Z])", "_", type).lower()  # Camel to snake case.
        type = re.sub("_field$", "", type)
        return type
    except AttributeError:
        pass
    return "unknown"


def _get_field_value(field: Field, value: Any):
    # Get the display value for fields that have choices.
    choices = None
    if getattr(field, "choices", None):
        choices = dict(field.choices)  # type: ignore
    if getattr(getattr(field, "base_field", None), "choices", None):
        choices = dict(field.base_field.choices)  # type: ignore
    if choices:
        if type(value) is [].__class__:
            return ", ".join([choices.get(choice, "") for choice in value])  # type: ignore
        else:
            return choices.get(value, "")

    if isinstance(field, DateTimeField):
        value = datetime.datetime.fromisoformat(value)
    elif isinstance(field, DateField):
        value = datetime.date.fromisoformat(value)
    elif isinstance(field, TimeField):
        value = datetime.time.fromisoformat(value)

    return value
