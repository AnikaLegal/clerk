from django.db import models

from accounts.models import User

from .issue import Issue
from .timestamped import TimestampedModel


class NoteType:
    PARALEGAL = "PARALEGAL"
    REVIEW = "REVIEW"


class IssueNote(TimestampedModel):
    """
    A note, taken against a issue.
    """

    NOTE_CHOICES = (
        (NoteType.PARALEGAL, "Paralegal"),
        (NoteType.REVIEW, "Review"),
    )

    # The case that this note is for
    issue = models.ForeignKey(Issue, on_delete=models.CASCADE)

    # Who made the note
    creator = models.ForeignKey(User, on_delete=models.PROTECT)

    # What kind of note this is.
    note_type = models.CharField(max_length=32, choices=NOTE_CHOICES)

    # The text content of the note
    text = models.CharField(max_length=4096, blank=True, default="")

    # An optional event time, which can be interpreted based on what kind of note this is:
    #  - Review: the time to next review this case.
    event = models.DateTimeField(null=True, blank=True)

    # Actionstep ID
    actionstep_id = models.IntegerField(blank=True, null=True)
