from django.db import models
from django.contrib.postgres.fields import ArrayField
from django.contrib.contenttypes.fields import GenericRelation
from django.db import transaction

from accounts.models import User

from .issue import Issue
from .issue_note import IssueNote, NoteType
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
    @transaction.atomic
    def maybe_generate_event(issue: Issue, prev_issue: Issue):
        assert issue.pk == prev_issue.pk
        create_kwargs = {}
        event_types = []

        if issue.paralegal != prev_issue.paralegal:
            # Paralegal changed
            create_kwargs["prev_user"] = prev_issue.paralegal
            create_kwargs["next_user"] = issue.paralegal
            event_types.append(EventType.PARALEGAL)

        if issue.stage != prev_issue.stage:
            # Stage changed
            create_kwargs["prev_stage"] = prev_issue.stage
            create_kwargs["next_stage"] = issue.stage
            event_types.append(EventType.STAGE)

        if issue.is_open != prev_issue.is_open:
            # Open state changed
            create_kwargs["prev_is_open"] = prev_issue.is_open
            create_kwargs["next_is_open"] = issue.is_open
            event_types.append(EventType.OPEN)

        if event_types:
            create_kwargs["event_types"] = event_types
            create_kwargs["issue"] = issue
            event = IssueEvent.objects.create(**create_kwargs)
            IssueNote.objects.create(
                issue=issue,
                note_type=NoteType.EVENT,
                content_object=event,
            )

    def get_text(self):
        text = ""
        is_user_changed = self.prev_user is not None or self.next_user is not None
        is_stage_changed = self.prev_stage is not None or self.next_stage is not None
        is_open_changed = self.prev_is_open is not None or self.next_is_open is not None
        if is_user_changed:
            text += "Assigned paralegal changed"
            if self.prev_user:
                text += " from " + self.prev_user.get_full_name()
            if self.next_user:
                text += " to " + self.next_user.get_full_name() + "."
        if is_stage_changed:
            fmt_stage = lambda s: s.lower().replace("_", " ").capitalize() if s else s
            text += f" Stage changed"
            if self.prev_stage:
                prev_stage = fmt_stage(self.prev_stage)
                text += f" from {prev_stage}"

            next_stage = fmt_stage(self.next_stage)
            text += f" to {next_stage}."

        if is_open_changed:
            if self.prev_is_open:
                text += " Case closed."
            else:
                text += " Case re-opened."

        return text

    EVENT_CHOICES = (
        (EventType.PARALEGAL, "Paralegal assigned"),
        (EventType.STAGE, "Stage change"),
        (EventType.OPEN, "Open change"),
    )

    # Store previous and next values
    # This is kinda gross but I like it better than putting everything in a JSON
    prev_is_open = models.BooleanField(blank=True, null=True)
    next_is_open = models.BooleanField(blank=True, null=True)
    prev_stage = models.CharField(max_length=32, null=True, blank=True)
    next_stage = models.CharField(max_length=32, null=True, blank=True)
    prev_user = models.ForeignKey(
        User, null=True, blank=True, on_delete=models.SET_NULL, related_name="+"
    )
    next_user = models.ForeignKey(
        User, null=True, blank=True, on_delete=models.SET_NULL, related_name="+"
    )

    # The case that this event is for
    issue = models.ForeignKey(Issue, on_delete=models.CASCADE)

    # Any notes created for this event (usually just one)
    issue_notes = GenericRelation(IssueNote)

    # What kind of evet this is.
    event_types = ArrayField(
        models.CharField(max_length=32, choices=EVENT_CHOICES),
        default=list,
        blank=True,
    )

    # Optinal Actionstep ID, for file notes imported from Actionstep
    actionstep_id = models.IntegerField(blank=True, null=True)
