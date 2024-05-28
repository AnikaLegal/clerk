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
@mock.patch("task.tasks.notify_of_assignment")
def test_task_notify__single_notification_via_trigger(
    mock_notify,
    event_type,
    django_capture_on_commit_callbacks,
):
    """
    For all trigger event types, test that a single notification is sent when
    tasks are created.
    """
    event_stage = None
    if event_type == EventType.STAGE:
        event_stage = CaseStage.UNSTARTED

    trigger = TaskTriggerFactory(event=event_type, event_stage=event_stage)
    templates = TaskTemplateFactory.create_batch(randint(1, 3), trigger=trigger)

    with django_capture_on_commit_callbacks(execute=True):
        event = IssueEventFactory(event_type=event_type)
        if event_type == EventType.STAGE:
            event.next_stage = CaseStage.UNSTARTED
        event.save()

    # A single call to the notify method?
    mock_notify.assert_called_once()
    # notify_of_assignment takes a list of task ids to notify about. This should
    # match the number of templates used to create tasks.
    assert mock_notify.call_args and len(mock_notify.call_args.args[0]) == len(
        templates
    )


@pytest.mark.django_db
@pytest.mark.enable_signals
@mock.patch("task.tasks.notify_of_assignment")
def test_task_notify__notify_tasks_match_created_tasks(
    mock_notify,
    django_capture_on_commit_callbacks,
):
    """
    Test that the tasks we are notifying about match the tasks that were created
    when the trigger was activated.
    """
    paralegal = UserFactory()
    issue = IssueFactory(paralegal=paralegal)

    trigger = TaskTriggerFactory(
        event=EventType.CREATE, tasks_assignment_role=TasksCaseRole.PARALEGAL
    )
    templates = TaskTemplateFactory.create_batch(randint(2, 4), trigger=trigger)

    with django_capture_on_commit_callbacks(execute=True):
        event = IssueEventFactory(event_type=EventType.CREATE, issue=issue)
        event.save()

    mock_notify.assert_called_once()
    notify_task_pks = mock_notify.call_args.args[0]

    tasks = Task.objects.filter(
        issue=issue, assigned_to=paralegal, owner=paralegal, template__in=templates
    )
    created_task_pks = [t.pk for t in tasks]

    assert sorted(created_task_pks) == sorted(notify_task_pks)


@pytest.mark.django_db
@pytest.mark.enable_signals
@mock.patch("task.notify.notify_user_of_assignment")
def test_task_notify__notify_tasks_match_created_tasks_for_multiple_users(
    mock_notify,
    django_capture_on_commit_callbacks,
):
    """
    Test that a single notification is sent to each assigned user when multiple
    tasks are created via a trigger.
    """
    lawyer = UserFactory()
    paralegal = UserFactory()
    issue = IssueFactory(lawyer=lawyer, paralegal=paralegal)

    lawyer_trigger = TaskTriggerFactory(
        event=EventType.CREATE, tasks_assignment_role=TasksCaseRole.LAWYER
    )
    TaskTemplateFactory.create_batch(randint(2, 4), trigger=lawyer_trigger)

    paralegal_trigger = TaskTriggerFactory(
        event=EventType.CREATE, tasks_assignment_role=TasksCaseRole.PARALEGAL
    )
    TaskTemplateFactory.create_batch(randint(2, 4), trigger=paralegal_trigger)

    with django_capture_on_commit_callbacks(execute=True):
        event = IssueEventFactory(event_type=EventType.CREATE, issue=issue)
        event.save()

    assert mock_notify.call_count == 2
    for call in mock_notify.mock_calls:
        notify_user = call.args[0]
        notify_tasks = call.args[1]

        assert notify_user in (lawyer, paralegal)
        if notify_user == lawyer:
            created_tasks = Task.objects.filter(
                issue=issue, assigned_to=lawyer, owner=lawyer
            )
        else:
            created_tasks = Task.objects.filter(
                issue=issue, assigned_to=paralegal, owner=paralegal
            )
        created_task_pks = [t.pk for t in created_tasks]
        notify_task_pks = [t.pk for t in notify_tasks]
        assert sorted(notify_task_pks) == sorted(created_task_pks)
