from django.db import models
from core.models.timestamped import TimestampedModel
from core.models.issue import CaseTopic, CaseStage
from django.core.exceptions import ValidationError


class TaskTriggerEvent(models.TextChoices):
    """
    Events that trigger the creation of a task.

    Future considerations may be:
    - case first created
    - case open/closed change
    - case assignment change
    - case outcome change
    - email received
    """

    STAGE_CHANGE = "STAGE_CHANGE", "Stage changed"


class TaskTriggerAssignee(models.TextChoices):
    """
    Who gets assigned the task.
    """

    ASSIGNED_PARALEGAL = "ASSIGNED_PARALEGAL", "Assigned paralegal"
    ASSIGNED_LAWYER = "ASSIGNED_LAWYER", "Assigned lawyer"
    COORDINATORS = "COORDINATORS", "Coordinators"


class TaskTrigger(TimestampedModel):
    topic = models.CharField(max_length=32, choices=CaseTopic.ACTIVE_CHOICES)
    event = models.CharField(
        max_length=32,
        choices=TaskTriggerEvent.choices,
        default=TaskTriggerEvent.STAGE_CHANGE,
    )
    # Only relevant when event is STAGE_CHANGED
    event_stage = models.CharField(
        max_length=32, choices=CaseStage.CHOICES, blank=True, default=""
    )
    assignee = models.CharField(max_length=32, choices=TaskTriggerAssignee.choices)

    def clean(self):
        if self.event == TaskTriggerEvent.STAGE_CHANGE and not self.event_stage:
            raise ValidationError(
                'The {0} field cannot be empty when the {1} field is "{2}"'.format(
                    TaskTrigger._meta.get_field("event_stage").verbose_name,
                    TaskTrigger._meta.get_field("event").verbose_name,
                    TaskTriggerEvent.STAGE_CHANGE.label,
                )
            )

    class Meta:
        verbose_name = "trigger"
