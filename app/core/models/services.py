from django.db import models
from django.utils import timezone

from .issue import Issue
from .timestamped import TimestampedModel


class LegalServiceType(models.TextChoices):
    DISCRETE = "DISCRETE", "Discrete legal service"
    ONGOING = "ONGOING", "Ongoing legal service"


class DiscreteLegalServiceSubtype(models.TextChoices):
    ADVICE = "ADVICE", "Legal advice"
    TASK = "TASK", "Legal task"
    INFORMATION = "INFORMATION", "Information"  # TODO: Use "Legal information"
    REFERRAL = (
        "REFERRAL",
        "Referral",
    )  # TODO: what does S/W mean? see whiteboard images.


class OngoingLegalServiceSubtype(models.TextChoices):
    CASEWORK = "CASEWORK", "Ongoing legal casework"
    COURT_REPRESENTATION = "COURT_REPRESENTATION", "Court or tribunal representation"
    OTHER_REPRESENTATION = "OTHER_REPRESENTATION", "Other representation services"


class LegalService(TimestampedModel):
    """
    The legal services provided relating to a specific issue.
    """

    type = models.CharField(max_length=32, choices=LegalServiceType.choices)
    sub_type = models.CharField(
        max_length=32,
        choices=DiscreteLegalServiceSubtype.choices
        + OngoingLegalServiceSubtype.choices,
    )
    issue = models.ForeignKey(Issue, on_delete=models.CASCADE)
    started_at = models.DateTimeField(default=timezone.now)
    finished_at = models.DateTimeField(null=True, blank=True)
    notes = models.TextField(null=True, blank=True)
