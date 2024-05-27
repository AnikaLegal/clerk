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
    Test task trigger activates and tasks are created for each issue event type.
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

    assert Task.objects.filter(
        issue=event.issue, template__in=templates
    ).count() == len(templates)


@pytest.mark.django_db
@pytest.mark.enable_signals
@pytest.mark.parametrize(
    "field_name, role",
    [("lawyer", TasksCaseRole.LAWYER), ("paralegal", TasksCaseRole.PARALEGAL)],
)
def test_task_trigger__tasks_assigned_correctly(
    field_name,
    role,
    django_capture_on_commit_callbacks,
):
    """ """
    user = UserFactory()
    kwargs = {field_name: user}
    issue = IssueFactory(**kwargs)

    trigger = TaskTriggerFactory(event=EventType.CREATE, tasks_assignment_role=role)
    templates = TaskTemplateFactory.create_batch(randint(1, 3), trigger=trigger)

    with django_capture_on_commit_callbacks(execute=True):
        event = IssueEventFactory(event_type=EventType.CREATE, issue=issue)
        event.save()

    assert Task.objects.filter(
        issue=issue, assigned_to=user, owner=user
    ).count() == len(templates)


# NOTE: As we are using the actual Anika coordinator email we make sure that,
# even though notifications are disabled when testing, we don't send out a
# notification by patching the notify method. This helps protect us from future
# changes that might accidentally enable sending notifications when testing.
@pytest.mark.django_db
@pytest.mark.enable_signals
@mock.patch("task.notify.notify_user")
def test_task_trigger__tasks_assigned_correctly_to_coordinators(
    mock_notify,
    django_capture_on_commit_callbacks,
):
    """ """
    user = UserFactory(email="coordinators@anikalegal.com")
    issue = IssueFactory()

    trigger = TaskTriggerFactory(
        event=EventType.CREATE, tasks_assignment_role=TasksCaseRole.COORDINATOR
    )
    templates = TaskTemplateFactory.create_batch(randint(1, 3), trigger=trigger)

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


@pytest.mark.django_db
@pytest.mark.enable_signals
def test_task_trigger__tasks_assigned_correctly_with_multiple_triggers(
    django_capture_on_commit_callbacks,
):
    """
    Test that task assignment is correct when there are multiple triggers that
    assign tasks to different roles.
    """
    lawyer = UserFactory()
    paralegal = UserFactory()
    issue = IssueFactory(lawyer=lawyer, paralegal=paralegal)

    lawyer_trigger = TaskTriggerFactory(
        event=EventType.CREATE, tasks_assignment_role=TasksCaseRole.LAWYER
    )
    lawyer_templates = TaskTemplateFactory.create_batch(
        randint(1, 3), trigger=lawyer_trigger
    )

    paralegal_trigger = TaskTriggerFactory(
        event=EventType.CREATE, tasks_assignment_role=TasksCaseRole.PARALEGAL
    )
    paralegal_templates = TaskTemplateFactory.create_batch(
        randint(1, 3), trigger=paralegal_trigger
    )

    with django_capture_on_commit_callbacks(execute=True):
        event = IssueEventFactory(event_type=EventType.CREATE, issue=issue)
        event.save()

    # Tasks are created for each of the triggers, associated with the
    # appropriate templates and assigned to the correct users based on their
    # role?
    assert Task.objects.filter(
        issue=issue, assigned_to=lawyer, owner=lawyer, template__in=lawyer_templates
    ).count() == len(lawyer_templates)
    assert Task.objects.filter(
        issue=issue,
        assigned_to=paralegal,
        owner=paralegal,
        template__in=paralegal_templates,
    ).count() == len(paralegal_templates)
