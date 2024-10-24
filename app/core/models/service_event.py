from accounts.models import User
from django.contrib.contenttypes.fields import GenericRelation
from django.db import models

from .issue_note import IssueNote
from .service import Service, ServiceCategory, DiscreteServiceType, OngoingServiceType
from .timestamped import TimestampedModel


class EventType(models.TextChoices):
    CREATE = "CREATE", "Service created"
    UPDATE = "UPDATE", "Service updated"
    DELETE = "DELETE", "Service deleted"


class ServiceEvent(TimestampedModel):
    """
    An event that occurs on a service.
    """

    event_type = models.CharField(max_length=32, choices=EventType)
    service = models.ForeignKey(Service, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.PROTECT, related_name="+")
    issue_notes = GenericRelation(IssueNote)

    def get_text(self) -> str:
        name = self.user.get_full_name()
        match self.event_type:
            case EventType.CREATE:
                verb = "added"
            case EventType.UPDATE:
                verb = "updated"
            case EventType.DELETE:
                verb = "deleted"
            case _:
                raise Exception(f"Unhandled event type: {self.event_type}")

        service = self.service
        category_lower = service.category.lower()
        indefinite_article = (
            "an" if category_lower[0] in ("a", "e", "i", "o", "u") else "a"
        )
        text = f"{name} {verb} {indefinite_article} {category_lower} service:\n"

        type = service.type
        if type in DiscreteServiceType:
            type_label = DiscreteServiceType[type].label
        else:
            type_label = OngoingServiceType[type].label
        text += f"- Type: {type_label}\n"

        match service.category:
            case ServiceCategory.DISCRETE:
                text += f"- Date: {service.started_at}\n"
                if service.count:
                    text += f"- Count: {service.count}\n"
            case ServiceCategory.ONGOING:
                text += f"- Start date: {service.started_at}\n"
                if service.finished_at:
                    text += f"- Finish date: {service.finished_at}\n"

        if service.notes:
            text += f"- Notes: {service.notes}\n"

        return text
