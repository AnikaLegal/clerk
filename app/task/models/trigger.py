from django.db import models
from core.models import TimestampedModel
from core.models.issue import CaseTopic, CaseStage
from core.models.issue_event import EventType
from django.core.exceptions import ValidationError
from django.db.models import Q, F


class TriggerTopic(CaseTopic):
    ANY = "ANY"
    ACTIVE_CHOICES = [(ANY, "Any"), *CaseTopic.ACTIVE_CHOICES]


class TasksAssignedTo(models.TextChoices):
    """
    Who gets assigned the task(s).
    """

    PARALEGAL = "PARALEGAL", "The case paralegal"
    LAWYER = "LAWYER", "The case lawyer"
    COORDINATOR = "COORDINATOR", "Coordinators"


class TaskTrigger(TimestampedModel):
    topic = models.CharField(max_length=32, choices=TriggerTopic.ACTIVE_CHOICES)
    event = models.CharField(max_length=32, choices=EventType.choices)
    # Only relevant when event is STAGE
    event_stage = models.CharField(
        max_length=32, choices=CaseStage.CHOICES, blank=True, null=True, default=None
    )
    tasks_assigned_to = models.CharField(max_length=32, choices=TasksAssignedTo.choices)

    class Meta:
        constraints = [
            models.CheckConstraint(
                check=~Q(event=EventType.STAGE) | Q(event_stage__isnull=False),
                name="%(app_label)s_%(class)s_event_stage_required",
                # TODO: enable below on django version >= 4.1
                # violation_error_message='Event stage is required when the event is "{}"'.format(
                #    EventType.STAGE.label
                # ),
            ),
        ]
        verbose_name = "trigger"
