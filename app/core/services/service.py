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


def update_timeline(
    type: ServiceChangeType, service: ServiceDict, user_id: int, created_at: str
) -> bool:
    user = User.objects.get(id=user_id)
    IssueNote.objects.create(
        issue_id=service["issue_id"],
        note_type=NoteType.EVENT,
        text=_get_text(type, service, user),
        created_at=created_at,
    )
    return True


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
    indefinite_article = "an" if category[0] in ("a", "e", "i", "o", "u") else "a"

    text = (
        f"{name} {verb} {indefinite_article} {category} service:\n"
        + _get_service_text(service)
    )
    return text


def _get_service_text(service: ServiceDict):
    category = service["category"]
    type = service["type"]
    started_at = service["started_at"]

    count = service.get("count")
    finished_at = service.get("finished_at")

    if type in DiscreteServiceType:
        type_label = DiscreteServiceType[type].label
    else:
        type_label = OngoingServiceType[type].label

    text = f"- Type: {type_label}\n"

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
