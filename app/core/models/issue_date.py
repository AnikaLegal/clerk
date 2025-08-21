from accounts.models import User
from auditlog.registry import auditlog
from django.db import models

from .issue import Issue
from .timestamped import TimestampedModel


class DateType(models.TextChoices):
    FILING_DEADLINE = "FILING_DEADLINE", "Filing deadline"
    HEARING_LISTED = "HEARING_LISTED", "Hearing listed"
    NTV_TERMINATION = "NTV_TERMINATION", "NTV termination"
    OTHER = "OTHER", "Other"


class IssueDate(TimestampedModel):
    """
    Model representing a date associated with an issue.
    """

    issue = models.ForeignKey(Issue, on_delete=models.CASCADE)
    type = models.CharField(max_length=32, choices=DateType.choices)
    date = models.DateField()
    notes = models.TextField(blank=True, default="")
    is_reviewed = models.BooleanField(default=False)

    class Meta(TimestampedModel.Meta):
        verbose_name = "critical date"

    def check_permission(self, user: User) -> bool:
        """
        Returns True if the user has object level permission to access this instance.
        """
        return self.issue.paralegal_id == user.pk

    @staticmethod
    def audit_event_ignore_fields() -> set:
        return {IssueDate.issue.field.name}


auditlog.register(
    IssueDate,
    exclude_fields=["created_at", "modified_at"],
    serialize_data=True,
)
