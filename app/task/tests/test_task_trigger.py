import pytest
from unittest import mock
from random import randint

from core.factories import IssueEventFactory, IssueFactory, UserFactory
from core.models.issue import CaseStage
from core.models.issue_event import EventType
from task.factories import TaskTriggerFactory, TaskTemplateFactory
from task.models import Task
from task.models.trigger import TasksCaseRole


EVENT_TYPES = [c[0] for c in EventType.choices]


@pytest.mark.django_db
@pytest.mark.enable_signals
@pytest.mark.parametrize("event_type", EVENT_TYPES)
def test_task_trigger__tasks_created_on_issue_events(
    event_type,
    django_capture_on_commit_callbacks,
):
    """
    Test task trigger activates and tasks are created when an issue is created.
    """
    event_stage = None
    if event_type == EventType.STAGE:
        event_stage = CaseStage.UNSTARTED

    trigger = TaskTriggerFactory(event=event_type, event_stage=event_stage)
    templates = TaskTemplateFactory.create_batch(randint(1, 10), trigger=trigger)

    with django_capture_on_commit_callbacks(execute=True):
        event = IssueEventFactory(event_type=event_type)
        if event_type == EventType.STAGE:
            event.next_stage = CaseStage.UNSTARTED
        event.save()

    assert Task.objects.filter(issue=event.issue).count() == len(templates)


@pytest.mark.django_db
@pytest.mark.enable_signals
@pytest.mark.parametrize(
    "user_field_name, role",
    [("lawyer", TasksCaseRole.LAWYER), ("paralegal", TasksCaseRole.PARALEGAL)],
)
def test_task_trigger__tasks_assigned_correctly(
    user_field_name,
    role,
    django_capture_on_commit_callbacks,
):
    """ """
    user = UserFactory()
    kwargs = {user_field_name: user}
    issue = IssueFactory(**kwargs)

    trigger = TaskTriggerFactory(event=EventType.CREATE, tasks_assignment_role=role)
    templates = TaskTemplateFactory.create_batch(randint(1, 10), trigger=trigger)

    with django_capture_on_commit_callbacks(execute=True):
        event = IssueEventFactory(event_type=EventType.CREATE, issue=issue)
        event.save()

    assert Task.objects.filter(issue=event.issue, assigned_to=user).count() == len(
        templates
    )


# NOTE: As we are using the actual Anika coordinator email we make sure that,
# even though notifications are disabled when testing, we don't send out a
# notification by patching the notify method. This helps protect us from future
# changes that might accidentally enable sending notifications when testing.
@pytest.mark.django_db
@pytest.mark.enable_signals
@mock.patch("task.notify.notify_user")
def test_task_trigger__tasks_assigned_correctly_to_coordinators(mock_notify,
    django_capture_on_commit_callbacks,
):
    """ """
    user = UserFactory(email="coordinators@anikalegal.com")
    issue = IssueFactory()

    trigger = TaskTriggerFactory(
        event=EventType.CREATE, tasks_assignment_role=TasksCaseRole.COORDINATOR
    )
    templates = TaskTemplateFactory.create_batch(randint(1, 10), trigger=trigger)

    with django_capture_on_commit_callbacks(execute=True):
        event = IssueEventFactory(event_type=EventType.CREATE, issue=issue)
        event.save()

    assert Task.objects.filter(issue=event.issue, assigned_to=user).count() == len(
        templates
    )

    # NOTE: Not necessary for the test case. Helps catch a change in the code
    # that notifies when a task is assigned and consequently prevent
    # accidentally sending notifications (see note above).
    mock_notify.assert_called_once()