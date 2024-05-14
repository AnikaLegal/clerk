from django.db.models import Q, QuerySet
from accounts.models import User, CaseGroups
from core.models import Issue, IssueEvent
from core.models.issue_event import EventType
from task.models import Task, TaskTrigger
from task.models.trigger import TriggerTopic


def get_open_tasks_by_user(issue: Issue, user: User) -> QuerySet[Task]:
    """
    Return open tasks associated with the supplied issue and owned by or
    assigned to the supplied user.
    """
    return Task.objects.filter(issue=issue, is_open=True).filter(
        Q(owner=user) | Q(assigned_to=user)
    )


def get_triggers_by_issue_event(event: IssueEvent) -> QuerySet[TaskTrigger]:
    """
    Return tasks triggers corresponding to the supplied event.
    """
    queryset = TaskTrigger.objects.filter(event=event.event_type)
    queryset = queryset.filter(topic__in=[event.issue.topic, TriggerTopic.ANY])
    if event.event_type == EventType.STAGE:
        queryset = queryset.filter(event_stage=event.next_stage)
    return queryset


def is_user_assigned_to_issue(issue: Issue, user: User) -> bool:
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


def is_user_changed(event: IssueEvent) -> bool:
    """
    True if the supplied event represents a change to a previously set paralegal
    or lawyer.
    """
    return is_user_event(event) and event.prev_user_id


def is_user_removed(event: IssueEvent) -> bool:
    """
    True if the supplied event represents the removal of the paralegal or lawyer.
    """
    return is_user_event(event) and not event.next_user_id


def is_user_event(event: IssueEvent) -> bool:
    """
    True if the supplied event represents any change to the paralegal or lawyer.
    """
    return event.event_type in [EventType.PARALEGAL, EventType.LAWYER]
