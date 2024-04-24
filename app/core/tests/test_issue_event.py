import pytest

from core.factories import IssueFactory
from core.models import IssueEvent
from core.models.issue_event import EventType

# TODO: add tests for other event types.


@pytest.mark.django_db
@pytest.mark.enable_signals
def test_issue_event_created_on_issue_create():
    """
    Ensure an issue event is created when an issue is created.
    """
    issue = IssueFactory()

    assert IssueEvent.objects.count() == 1
    assert IssueEvent.objects.last().event_type == EventType.CREATE
