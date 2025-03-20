from accounts.models import CaseGroups
from core.models import Issue, IssueEvent
from core.models.issue_event import EventType
from accounts.models import User


def get_coordinators_user() -> User:
    """
    Get or create the user to which we assign coordinator tasks.
    """
    user, _ = User.objects.get_or_create(
        email="coordinators@anikalegal.com",
        defaults={
            "username": "coordinators@anikalegal.com",
            "first_name": "Paralegal",
            "last_name": "Coordinators",
        },
    )
    return user


def is_lawyer_acting_as_paralegal(issue: Issue) -> bool:
    """
    True if the user assigned as the paralegal is a member of the lawyer group.
    """
    return (
        issue.paralegal_id
        and issue.paralegal.groups.filter(name=CaseGroups.LAWYER).exists()
    )


def is_case_closed(event: IssueEvent) -> bool:
    """
    True if the supplied event represents a case closure.
    """
    return (
        event.event_type == EventType.OPEN
        and event.prev_is_open is not False
        and event.next_is_open is False
    )


def is_user_added(event: IssueEvent) -> bool:
    """
    True if the supplied event represents a change to a previously unassigned
    paralegal or lawyer.
    """
    return (
        is_user_event(event)
        and event.prev_user_id is None
        and event.next_user_id is not None
    )


def is_user_changed(event: IssueEvent) -> bool:
    """
    True if the supplied event represents a change to a previously assigned
    paralegal or lawyer.
    """
    return (
        is_user_event(event)
        and event.prev_user_id is not None
        and event.next_user_id is not None
        and event.prev_user_id != event.next_user_id
    )


def is_user_removed(event: IssueEvent) -> bool:
    """
    True if the supplied event represents the removal of the assigned paralegal
    or lawyer.
    """
    return (
        is_user_event(event)
        and event.prev_user_id is not None
        and event.next_user_id is None
    )


def is_user_event(event: IssueEvent) -> bool:
    """
    True if the supplied event represents any change to the paralegal or lawyer.
    """
    return event.event_type in [EventType.PARALEGAL, EventType.LAWYER]
