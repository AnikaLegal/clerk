import logging
from enum import Enum, auto
from typing import NotRequired, TypedDict

from accounts.models import User
from core.models.issue_note import IssueNote, NoteType
from core.models.service import DiscreteServiceType, OngoingServiceType, ServiceCategory


class ServiceDict(TypedDict):
    category: str
    type: str
    issue_id: str
    started_at: str
    finished_at: NotRequired[str]
    count: NotRequired[int]


class ServiceChangeType(Enum):
    CREATE = auto()
    UPDATE = auto()
    DELETE = auto()


logger = logging.getLogger(__file__)


def update_timeline(type: ServiceChangeType, service: ServiceDict, user: User):
    try:
        IssueNote.objects.create(
            issue_id=service["issue_id"],
            note_type=NoteType.EVENT,
            text=_get_text(type, service, user),
        )
    except Exception as e:
        logger.exception(e)


def _get_text(type: ServiceChangeType, service: ServiceDict, user: User):
    name = user.get_full_name()
    match type:
        case ServiceChangeType.CREATE:
            verb = "added"
        case ServiceChangeType.UPDATE:
            verb = "updated"
        case ServiceChangeType.DELETE:
            verb = "deleted"
    category = service["category"].lower()
    text = f"{name} {verb} a {category} service:\n" + _get_service_text(service)
    return text


def _get_service_text(service: ServiceDict):
    category = service["category"]
    type = service["type"]
    started_at = service["started_at"]

    count = service.get("count")
    finished_at = service.get("finished_at")

    if type in DiscreteServiceType:
        type_display = DiscreteServiceType[type].label
    else:
        type_display = OngoingServiceType[type].label

    text = f"- Type: {type_display}\n"

    match category:
        case ServiceCategory.DISCRETE:
            text += f"- Date: {started_at}\n"
            if count:
                text += f"- Count: {count}\n"
        case ServiceCategory.ONGOING:
            text += f"- Start date: {started_at}\n"
            if finished_at:
                text += f"- Finish date: {finished_at}\n"

    return text