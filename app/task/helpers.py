from accounts.models import User, CaseGroups
from core.models import Issue, IssueEvent
from core.models.issue_event import EventType


def is_user_assigned_to_issue(issue: Issue, user: User | None) -> bool:
    """
    True if the supplied user is assigned as the paralegal or lawyer on the
    supplied issue.
    """
    return (issue.lawyer_id and issue.lawyer == user) or (
        issue.paralegal_id and issue.paralegal == user
    )


def is_lawyer_acting_as_paralegal(issue: Issue) -> bool:
    """
    True if the user assigned as the paralegal is a member of the lawyer group.
    """
    return (
        issue.paralegal_id
        and issue.paralegal.groups.filter(name=CaseGroups.LAWYER).exists()
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
