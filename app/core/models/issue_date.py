from accounts.models import User
from auditlog.registry import auditlog
from django.db import models

from .issue import Issue
from .timestamped import TimestampedModel


class DateType(models.TextChoices):
    FILING_DEADLINE = "FILING_DEADLINE", "Filing deadline"
    HEARING_LISTED = "HEARING_LISTED", "Hearing listed"
    LIMITATION = "LIMITATION", "Limitation"
    NTV_TERMINATION = "NTV_TERMINATION", "NTV termination"
    OTHER = "OTHER", "Other"


class HearingType(models.TextChoices):
    IN_PERSON = "IN_PERSON", "In person"
    VIRTUAL = "VIRTUAL", "Virtual"


class IssueDate(TimestampedModel):
    """
    Model representing a date associated with an issue.
    """

    issue = models.ForeignKey(Issue, on_delete=models.CASCADE)
    type = models.CharField(max_length=32, choices=DateType.choices)
    date = models.DateField()
    notes = models.TextField(blank=True, default="")
    is_reviewed = models.BooleanField(default=False)

    hearing_type = models.CharField(
        max_length=32, choices=HearingType.choices, blank=True, default=""
    )
    # Name / address of physical location or link to virtual space.
    hearing_location = models.TextField(blank=True, default="")

    class Meta(TimestampedModel.Meta):
        verbose_name = "critical date"

    def save(self, *args, **kwargs):
        if self.type != DateType.HEARING_LISTED:
            self.hearing_type = ""
            self.hearing_location = ""
        return super().save(*args, **kwargs)

    def check_permission(self, user: User) -> bool:
        """
        Returns True if the user has object level permission to access this instance.
        """
        return self.issue.paralegal_id == user.pk

    @staticmethod
    def audit_event_ignore_fields() -> set:
        # Ignore the issue field in audit events.
        return {IssueDate.issue.field.name}


auditlog.register(
    IssueDate,
    exclude_fields=["created_at", "modified_at"],
    serialize_data=True,
)
