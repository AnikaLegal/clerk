from django.db import models
from core.models.timestamped import TimestampedModel
from core.models.issue import CaseTopic, CaseStage

NOTIFY_TOPIC_CHOICES = [
    ("GENERAL", "General"),
    *CaseTopic.ACTIVE_CHOICES,
]


class NotifyEvent(models.TextChoices):
    """
    Events that can trigger a notification.

    Future considerations may be:
    - case first created
    - case open/closed change
    - case assignment change
    - case outcome change
    - email received
    """

    STAGE_CHANGE = "STAGE_CHANGE", "Stage changed"


class NotifyChannel(models.TextChoices):
    """
    Channels which can be used to notify a user.

    Future considerations may be:
    - email
    - in-app notification systems
    """

    SLACK = "SLACK", "Send a Slack message"


class NotifyTarget(models.TextChoices):
    """
    Who gets notified about the event.
    """

    PARALEGAL = "PARALEGAL", "Assigned paralegal"
    LAWYER = "LAWYER", "Assigned lawyer"


class Notification(TimestampedModel):
    """
    A notification that is sent,
    triggered by an Issue event,
    sending text to a target user via a channel
    """

    name = models.CharField(max_length=64)
    topic = models.CharField(max_length=32, choices=NOTIFY_TOPIC_CHOICES)
    event = models.CharField(max_length=32, choices=NotifyEvent.choices)
    channel = models.CharField(max_length=32, choices=NotifyChannel.choices)
    target = models.CharField(max_length=32, choices=NotifyTarget.choices)
    raw_text = models.TextField()
    message_text = models.TextField()

    # Only relevant when event is STAGE_CHANGED
    event_stage = models.CharField(
        max_length=32, choices=CaseStage.CHOICES, blank=True, default=""
    )
