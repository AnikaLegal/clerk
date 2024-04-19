from django.db import models
from core.models.timestamped import TimestampedModel
from core.models.issue import CaseTopic, CaseStage
from django.core.exceptions import ValidationError

TASK_TRIGGER_TOPICS = [
    ("ANY", "Any"),
    *CaseTopic.ACTIVE_CHOICES,
]

class TaskTriggerEvent(models.TextChoices):
    """
    Events that trigger the creation of a task.

    Future considerations may be:
    - case first created
    - case open/closed change
    - case outcome change
    - email received
    """

    CASE_LAWYER_ASSIGN = "CASE_LAWYER_ASSIGN", "Case lawyer assigned"
    CASE_PARALEGAL_ASSIGN = "CASE_PARALEGAL_ASSIGN", "Case paralegal assigned"
    CASE_STAGE_CHANGE = "CASE_STAGE_CHANGE", "Case stage changed"


class TaskTriggerAssignedTo(models.TextChoices):
    """
    Who gets assigned the task.
    """

    USER_PARALEGAL = "USER_PARALEGAL", "The paralegal assigned to the case"
    USER_LAWYER = "USER_LAWYER", "The lawyer assigned to the case"
    GROUP_COORDINATOR = "GROUP_COORDINATOR", "Coordinators"


class TaskTrigger(TimestampedModel):
    topic = models.CharField(max_length=32, choices=TASK_TRIGGER_TOPICS)
    event = models.CharField(
        max_length=32,
        choices=TaskTriggerEvent.choices,
        default=TaskTriggerEvent.CASE_STAGE_CHANGE,
    )
    # Only relevant when event is STAGE_CHANGED
    event_stage = models.CharField(
        max_length=32, choices=CaseStage.CHOICES, blank=True, default=""
    )
    tasks_assigned_to = models.CharField(max_length=32, choices=TaskTriggerAssignedTo.choices)

    def clean(self):
        if self.event == TaskTriggerEvent.CASE_STAGE_CHANGE and not self.event_stage:
            raise ValidationError(
                'The {0} field cannot be empty when the {1} field is "{2}"'.format(
                    TaskTrigger._meta.get_field("event_stage").verbose_name,
                    TaskTrigger._meta.get_field("event").verbose_name,
                    TaskTriggerEvent.CASE_STAGE_CHANGE.label,
                )
            )

    class Meta:
        verbose_name = "trigger"
