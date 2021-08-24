from django.db import models

from .issue import Issue
from .timestamped import TimestampedModel


class EventType:
    # A paralegal has been assigned.
    PARALEGAL = "PARALEGAL"
    # The case stage has changed
    STAGE = "STAGE"
    # The case has opened/closed
    OPEN = "OPEN"


class IssueEvent(TimestampedModel):
    """
    An event that happens for an issue.
    """

    @staticmethod
    def maybe_generate_event(issue: Issue, prev_issue: Issue):
        pass

    EVENT_CHOICES = (
        (EventType.PARALEGAL, "Paralegal assigned"),
        (EventType.STAGE, "Stage change"),
        (EventType.OPEN, "Open change"),
    )

    # The case that this event is for
    issue = models.ForeignKey(Issue, on_delete=models.CASCADE)

    # What kind of evet this is.
    event_type = models.CharField(max_length=32, choices=EVENT_CHOICES)

    # The text content of the note
    text = models.CharField(max_length=4096, blank=True, default="")

    # Optinal Actionstep ID, for file notes imported from Actionstep
    actionstep_id = models.IntegerField(blank=True, null=True)
