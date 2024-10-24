from django.db import models

from .issue import Issue
from .timestamped import TimestampedModel


class ServiceCategory(models.TextChoices):
    DISCRETE = "DISCRETE", "Discrete service"
    ONGOING = "ONGOING", "Ongoing service"


class DiscreteServiceType(models.TextChoices):
    LEGAL_ADVICE = "LEGAL_ADVICE", "Legal advice"
    LEGAL_TASK = "LEGAL_TASK", "Legal task"
    GENERAL_INFORMATION = "GENERAL_INFORMATION", "Information"
    GENERAL_REFERRAL_SIMPLE = (
        "GENERAL_REFERRAL_SIMPLE",
        "Referral (Simple)",
    )
    GENERAL_REFERRAL_FACILITATED = (
        "GENERAL_REFERRAL_FACILITATED",
        "Referral (Facilitated)",
    )


class OngoingServiceType(models.TextChoices):
    LEGAL_SUPPORT = (
        "LEGAL_SUPPORT",
        "Legal support",
    )
    REPRESENTATION_COURT_TRIBUNAL = (
        "REPRESENTATION_COURT_TRIBUNAL",
        "Court or tribunal representation",
    )
    REPRESENTATION_OTHER = "REPRESENTATION_OTHER", "Other representation"


class Service(TimestampedModel):
    """
    A unit of legal or non-legal work relating to a specific issue.
    """

    category = models.CharField(max_length=32, choices=ServiceCategory)
    type = models.CharField(
        max_length=64,
        choices=DiscreteServiceType.choices + OngoingServiceType.choices,
    )
    issue = models.ForeignKey(Issue, on_delete=models.CASCADE)
    started_at = models.DateField()
    notes = models.TextField(null=True, blank=True)

    # Category specific fields.
    count = models.IntegerField(default=1)
    finished_at = models.DateField(null=True, blank=True)

    # Internal status fields.

    # Used for soft delete. We want to keep the service around because we use it
    # to dynamically supply the text for associated issue notes. See the
    # ServiceEvent model.
    is_deleted = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        # Ensure count is always one for ongoing services.
        if self.category == ServiceCategory.ONGOING:
            self.count = 1
        return super().save(*args, **kwargs)
