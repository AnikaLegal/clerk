from django.db import models
from core.models import TimestampedModel
from core.models.issue import CaseTopic, CaseStage
from core.models.issue_event import EventType


class TriggerTopic(CaseTopic):
    ANY = "ANY"
    choices = [(ANY, "Any"), *CaseTopic.ACTIVE_CHOICES]


class TasksCaseRole(models.TextChoices):
    """
    The role of the user assigned to the task(s).
    """

    PARALEGAL = "PARALEGAL", "Paralegal"
    LAWYER = "LAWYER", "Lawyer"
    COORDINATOR = "COORDINATOR", "Coordinators"


class TaskTrigger(TimestampedModel):
    name = models.CharField(max_length=128)
    topic = models.CharField(max_length=32, choices=TriggerTopic.choices)
    event = models.CharField(max_length=32, choices=EventType.choices)
    # Only relevant when event is STAGE
    event_stage = models.CharField(
        max_length=32, choices=CaseStage.CHOICES, blank=True, null=True, default=None
    )
    tasks_assignment_role = models.CharField(
        max_length=32, choices=TasksCaseRole.choices
    )

    class Meta:
        verbose_name = "trigger"
