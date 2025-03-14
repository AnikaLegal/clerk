from accounts.models import User
from django.contrib.contenttypes.fields import GenericRelation
from django.core.serializers.json import DjangoJSONEncoder
from django.db import models
from django.template.loader import render_to_string
from rest_framework import serializers

from .issue_note import IssueNote
from .service import Service, ServiceCategory
from .timestamped import TimestampedModel


class _ServiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Service
        fields = "__all__"

    issue = serializers.PrimaryKeyRelatedField(read_only=True)


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

    # We need to save the details of the service at the point in time the event
    # occurred so we use the appropriate values when we generate the text for
    # this event (see get_text method)
    service_at_event = models.JSONField(encoder=DjangoJSONEncoder)

    def save(self, *args, **kwargs):
        serializer = _ServiceSerializer(self.service)
        self.service_at_event = serializer.data
        return super().save(*args, **kwargs)

    def get_text(self) -> str:
        name = self.user.get_full_name()
        match self.event_type:
            case EventType.CREATE:
                verb = "added"
            case EventType.DELETE:
                verb = "deleted"
            case EventType.UPDATE:
                verb = "updated"
            case _:
                raise Exception(f"Unhandled event type: {self.event_type}")

        serializer = _ServiceSerializer(data=self.service_at_event)
        serializer.is_valid(raise_exception=True)
        service = Service(**serializer.validated_data)

        category_lower = service.category.lower()
        indefinite_article = (
            "an" if category_lower[0] in ("a", "e", "i", "o", "u") else "a"
        )

        context = {
            "intro": f"{name} {verb} {indefinite_article} {category_lower} service:",
            "service": service,
            "categories": {
                "discrete": ServiceCategory.DISCRETE,
                "ongoing": ServiceCategory.ONGOING,
            },
        }
        return render_to_string("case/service_event.html", context)
