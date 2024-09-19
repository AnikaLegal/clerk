from django.db import models
from django.utils import timezone

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
    The services provided relating to a specific issue.
    """

    category = models.CharField(max_length=32, choices=ServiceCategory)
    type = models.CharField(
        max_length=64,
        choices=DiscreteServiceType.choices + OngoingServiceType.choices,
    )
    issue = models.ForeignKey(Issue, on_delete=models.CASCADE)
    started_at = models.DateField(default=timezone.now)
    finished_at = models.DateField(null=True, blank=True)
    notes = models.TextField(null=True, blank=True)

    class Meta:
        constraints = [
            models.CheckConstraint(
                name="%(app_label)s_%(class)s_service_type_by_category",
                condition=(
                    (
                        models.Q(category=ServiceCategory.DISCRETE)
                        & models.Q(type__in=DiscreteServiceType)
                    )
                    | (
                        models.Q(category=ServiceCategory.ONGOING)
                        & models.Q(type__in=OngoingServiceType)
                    )
                ),
                violation_error_message="Service type does not belong to that service category",
            )
        ]
