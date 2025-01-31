from django.db import models
from django.contrib.contenttypes.fields import GenericRelation
from django.db import transaction

from accounts.models import User

from .issue import Issue
from .issue_note import IssueNote
from .timestamped import TimestampedModel


class EventType(models.TextChoices):
    # The case was created
    CREATE = "CREATE", "Created"
    # A supervising lawyer has been assigned.
    LAWYER = "LAWYER", "Lawyer assigned"
    # A paralegal has been assigned.
    PARALEGAL = "PARALEGAL", "Paralegal assigned"
    # The case stage has changed
    STAGE = "STAGE", "Stage change"
    # The case has opened/closed
    OPEN = "OPEN", "Open change"


class IssueEvent(TimestampedModel):
    """
    An event that happens for an issue.
    """

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

    event_type = models.CharField(max_length=32, choices=EventType.choices)

    # Optinal Actionstep ID, for file notes imported from Actionstep
    actionstep_id = models.IntegerField(blank=True, null=True)

    @staticmethod
    @transaction.atomic
    def maybe_generate_event(issue: Issue, prev_issue: Issue | None):
        assert prev_issue is None or issue.pk == prev_issue.pk
        create_kwargs_list = []
        event_types = []

        if not prev_issue:
            # Case created
            create_kwargs = {
                "next_is_open": issue.is_open,
                "next_stage": issue.stage,
            }
            create_kwargs_list.append(create_kwargs)
            event_types.append(EventType.CREATE)

            if issue.lawyer:
                # Lawyer changed
                create_kwargs = {
                    "next_user": issue.lawyer,
                }
                create_kwargs_list.append(create_kwargs)
                event_types.append(EventType.LAWYER)

            if issue.paralegal:
                # Paralegal changed
                create_kwargs = {
                    "next_user": issue.paralegal,
                }
                create_kwargs_list.append(create_kwargs)
                event_types.append(EventType.PARALEGAL)

            # TODO: check is_open & stage for changes from the default?
        else:
            if issue.lawyer != prev_issue.lawyer:
                # Lawyer changed
                create_kwargs = {
                    "prev_user": prev_issue.lawyer,
                    "next_user": issue.lawyer,
                }
                create_kwargs_list.append(create_kwargs)
                event_types.append(EventType.LAWYER)

            if issue.paralegal != prev_issue.paralegal:
                # Paralegal changed
                create_kwargs = {
                    "prev_user": prev_issue.paralegal,
                    "next_user": issue.paralegal,
                }
                create_kwargs_list.append(create_kwargs)
                event_types.append(EventType.PARALEGAL)

            if issue.is_open != prev_issue.is_open:
                # Open state changed
                create_kwargs = {
                    "prev_is_open": prev_issue.is_open,
                    "next_is_open": issue.is_open,
                    "prev_stage": prev_issue.stage,
                    "next_stage": issue.stage,
                }
                create_kwargs_list.append(create_kwargs)
                event_types.append(EventType.OPEN)
            elif issue.stage != prev_issue.stage:
                # Stage changed
                create_kwargs = {
                    "prev_stage": prev_issue.stage,
                    "next_stage": issue.stage,
                }
                create_kwargs_list.append(create_kwargs)
                event_types.append(EventType.STAGE)

        # TODO: Change in case outcome

        for event_type, create_kwargs in zip(event_types, create_kwargs_list):
            create_kwargs["event_type"] = event_type
            create_kwargs["issue"] = issue
            IssueEvent.objects.create(**create_kwargs)

    def get_text(self):
        is_user_changed = self.prev_user is not None or self.next_user is not None
        is_stage_changed = self.prev_stage is not None or self.next_stage is not None
        is_open_changed = self.prev_is_open is not None or self.next_is_open is not None
        if is_user_changed:
            is_changed = self.prev_user and self.next_user
            is_removed = self.prev_user and not self.next_user
            if self.event_type == EventType.LAWYER:
                role = "lawyer"

            elif self.event_type == EventType.PARALEGAL:
                role = "paralegal"
            else:
                role = "unknown"

            if is_changed:
                name = self.prev_user.get_full_name()
                new_name = self.next_user.get_full_name()
                return f"Assigned {role} changed from {name} to {new_name}."
            elif is_removed:
                name = self.prev_user.get_full_name()
                return f"Removed {name} from the {role} role."
            else:
                new_name = self.next_user.get_full_name()
                return f"Added {new_name} as the case {role}."

        texts = []
        if is_stage_changed:
            text = f"Stage changed"
            fmt_stage = lambda s: s.lower().replace("_", " ").capitalize() if s else s
            if self.prev_stage:
                prev_stage = fmt_stage(self.prev_stage)
                text += f" from {prev_stage}"

            next_stage = fmt_stage(self.next_stage)
            text += f" to {next_stage}."
            texts.append(text)

        if is_open_changed:
            if self.prev_is_open:
                texts.append("Case closed.")
            else:
                texts.append("Case re-opened.")

        text = " ".join(texts)
        return text if text else "Error: Unknown event."
