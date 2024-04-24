from django.db import models
from core.models import TimestampedModel
from core.models.issue import CaseTopic, CaseStage
from core.models.issue_event import EventType
from django.core.exceptions import ValidationError


class TaskTriggerTopic:
    ANY = "ANY"
    CHOICES = [(ANY, "Any"), *CaseTopic.ACTIVE_CHOICES]


class TaskTriggerAssignedTo(models.TextChoices):
    """
    Who gets assigned the task.
    """

    PARALEGAL = "PARALEGAL", "The paralegal assigned to the case"
    LAWYER = "LAWYER", "The lawyer assigned to the case"
    COORDINATOR = "COORDINATOR", "Coordinators"


class TaskTrigger(TimestampedModel):
    topic = models.CharField(max_length=32, choices=TaskTriggerTopic.CHOICES)
    event = models.CharField(
        max_length=32, choices=EventType.choices, default=EventType.STAGE
    )
    # Only relevant when event is STAGE_CHANGED
    event_stage = models.CharField(
        max_length=32, choices=CaseStage.CHOICES, blank=True, default=""
    )
    tasks_assigned_to = models.CharField(
        max_length=32, choices=TaskTriggerAssignedTo.choices
    )

    def clean(self):
        if self.event == EventType.STAGE and not self.event_stage:
            raise ValidationError(
                'The {0} field cannot be empty when the {1} field is "{2}"'.format(
                    TaskTrigger._meta.get_field("event_stage").verbose_name,
                    TaskTrigger._meta.get_field("event").verbose_name,
                    EventType.STAGE.label,
                )
            )

    class Meta:
        verbose_name = "trigger"
