from rest_framework import serializers
from django.urls import reverse

from notify.models import Notification, NotifyEvent, NotifyChannel, NotifyTarget
from .fields import TextChoiceField, LocalDateField


class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = (
            "id",
            "created_at",
            "name",
            "topic",
            "event",
            "event_stage",
            "channel",
            "target",
            "raw_text",
            "message_text",
            "url",
        )

    event = TextChoiceField(NotifyEvent)
    channel = TextChoiceField(NotifyChannel)
    target = TextChoiceField(NotifyTarget)
    url = serializers.SerializerMethodField()
    created_at = LocalDateField()

    def get_url(self, obj):
        return reverse("template-notify-detail", args=(obj.pk,))
