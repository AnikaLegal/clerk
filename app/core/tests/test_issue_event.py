import pytest
from unittest import mock

from core.factories import IssueFactory, UserFactory
from core.models import IssueEvent
from core.models.issue_event import EventType
from core.models.issue import CaseStage


@pytest.mark.django_db
@pytest.mark.enable_signals
def test_issue_event_created_on_issue_create():
    """
    Ensure an issue event is created when an issue is created.
    """
    issue = IssueFactory()

    events = IssueEvent.objects.filter(issue=issue)
    assert events.count() == 1
    assert events.last().event_type == EventType.CREATE


@pytest.mark.django_db
@pytest.mark.enable_signals
def test_issue_event_created_on_issue_lawyer():
    """
    Ensure an issue event is created when a lawyer is assigned, changed and
    removed from an issue.
    """
    user_1 = UserFactory()
    user_2 = UserFactory()
    event_type = EventType.LAWYER

    issue = IssueFactory(lawyer=user_1)

    events = IssueEvent.objects.filter(issue=issue, event_type=event_type)
    assert events.count() == 1
    event = events.last()
    assert event.prev_user is None
    assert event.next_user == user_1

    issue.lawyer = user_2
    issue.save()

    events = IssueEvent.objects.filter(issue=issue, event_type=event_type)
    assert events.count() == 2
    event = events.last()
    assert event.prev_user == user_1
    assert event.next_user == user_2

    issue.lawyer = None
    issue.save()

    events = IssueEvent.objects.filter(issue=issue, event_type=event_type)
    assert events.count() == 3
    event = events.last()
    assert event.prev_user == user_2
    assert event.next_user == None


# TODO: We have to mock these functions to prevent errors that occur when
# changing the paralegal. We should fix this so that the mocks are not required.
@mock.patch("core.signals.issue.add_user_to_case", autospec=True)
@mock.patch("core.signals.issue.remove_user_from_case", autospec=True)
@mock.patch("core.signals.issue.send_case_assignment_slack", autospec=True)
@pytest.mark.django_db
@pytest.mark.enable_signals
def test_issue_event_created_on_issue_paralegal(mock_add, mock_remove, mock_send):
    """
    Ensure an issue event is created when a paralegal is assigned, changed and
    removed from an issue.
    """
    user_1 = UserFactory()
    user_2 = UserFactory()
    event_type = EventType.PARALEGAL

    issue = IssueFactory(paralegal=user_1)

    events = IssueEvent.objects.filter(issue=issue, event_type=event_type)
    assert events.count() == 1
    event = events.last()
    assert event.prev_user is None
    assert event.next_user == user_1

    issue.paralegal = user_2
    issue.save()

    events = IssueEvent.objects.filter(issue=issue, event_type=event_type)
    assert events.count() == 2
    event = events.last()
    assert event.prev_user == user_1
    assert event.next_user == user_2

    issue.paralegal = None
    issue.save()

    events = IssueEvent.objects.filter(issue=issue, event_type=event_type)
    assert events.count() == 3
    event = events.last()
    assert event.prev_user == user_2
    assert event.next_user == None


@pytest.mark.django_db
@pytest.mark.enable_signals
def test_issue_event_created_on_issue_stage():
    """
    Ensure issue events are created when the case stage changes.
    """
    event_type = EventType.STAGE

    issue = IssueFactory()

    events = IssueEvent.objects.filter(issue=issue, event_type=event_type)
    assert events.count() == 0

    issue.stage = CaseStage.CLIENT_AGREEMENT
    issue.save()

    events = IssueEvent.objects.filter(issue=issue, event_type=event_type)
    assert events.count() == 1
    event = events.last()
    assert event.next_stage == issue.stage

    issue.stage = CaseStage.ADVICE
    issue.save()

    events = IssueEvent.objects.filter(issue=issue, event_type=event_type)
    assert events.count() == 2
    event = events.last()
    assert event.prev_stage == CaseStage.CLIENT_AGREEMENT
    assert event.next_stage == CaseStage.ADVICE

    issue.stage = CaseStage.FORMAL_LETTER
    issue.save()

    events = IssueEvent.objects.filter(issue=issue, event_type=event_type)
    assert events.count() == 3
    event = events.last()
    assert event.prev_stage == CaseStage.ADVICE
    assert event.next_stage == CaseStage.FORMAL_LETTER


@pytest.mark.django_db
@pytest.mark.enable_signals
def test_issue_event_created_on_issue_open():
    """
    Ensure issue events are created when the is opened & closed.
    """
    event_type = EventType.OPEN

    issue = IssueFactory()

    events = IssueEvent.objects.filter(issue=issue, event_type=event_type)
    assert events.count() == 0

    issue.is_open = False
    issue.stage = CaseStage.CLOSED
    issue.save()

    events = IssueEvent.objects.filter(issue=issue, event_type=event_type)
    assert events.count() == 1
    event = events.last()
    assert event.prev_is_open == True
    assert event.next_is_open == False
    assert event.prev_stage == CaseStage.UNSTARTED
    assert event.next_stage == CaseStage.CLOSED

    issue.is_open = True
    issue.stage = CaseStage.UNSTARTED
    issue.save()

    events = IssueEvent.objects.filter(issue=issue, event_type=event_type)
    assert events.count() == 2
    event = events.last()
    assert event.prev_is_open == False
    assert event.next_is_open == True
    assert event.prev_stage == CaseStage.CLOSED
    assert event.next_stage == CaseStage.UNSTARTED
