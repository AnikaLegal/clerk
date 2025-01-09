import pytest
from unittest import mock
from random import randint
from datetime import timedelta

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

    with django_capture_on_commit_callbacks(execute=True):
        event = IssueEventFactory(event_type=event_type)
        if event_type == EventType.STAGE:
            event.next_stage = CaseStage.UNSTARTED
        event.save()

    assert (
        Task.objects.filter(
            issue=event.issue, template__in=trigger.templates.all()
        ).count()
        == trigger.templates.count()
    )


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
    """
    Test task triggers assign created tasks to the correct user.
    """
    user = UserFactory()
    kwargs = {field_name: user}
    issue = IssueFactory(**kwargs)
    trigger = TaskTriggerFactory(event=EventType.CREATE, tasks_assignment_role=role)

    with django_capture_on_commit_callbacks(execute=True):
        event = IssueEventFactory(event_type=EventType.CREATE, issue=issue)
        event.save()

    assert (
        Task.objects.filter(issue=issue, assigned_to=user).count()
        == trigger.templates.count()
    )


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

    with django_capture_on_commit_callbacks(execute=True):
        event = IssueEventFactory(event_type=EventType.CREATE, issue=issue)
        event.save()

    assert (
        Task.objects.filter(issue=event.issue, assigned_to=user).count()
        == trigger.templates.count()
    )

    # NOTE: Not necessary for the test case. Helps catch changes to the
    # notification code and consequently prevent accidentally sending
    # notifications (see note above).
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
    paralegal_trigger = TaskTriggerFactory(
        event=EventType.CREATE, tasks_assignment_role=TasksCaseRole.PARALEGAL
    )

    with django_capture_on_commit_callbacks(execute=True):
        event = IssueEventFactory(event_type=EventType.CREATE, issue=issue)
        event.save()

    # Tasks are created for each of the triggers, associated with the
    # appropriate templates and assigned to the correct users based on their
    # role?
    assert (
        Task.objects.filter(
            issue=issue,
            assigned_to=lawyer,
            template__in=lawyer_trigger.templates.all(),
        ).count()
        == lawyer_trigger.templates.count()
    )
    assert (
        Task.objects.filter(
            issue=issue,
            assigned_to=paralegal,
            template__in=paralegal_trigger.templates.all(),
        ).count()
        == paralegal_trigger.templates.count()
    )


@pytest.mark.django_db
@pytest.mark.enable_signals
def test_task_template__due_date_set_correctly(
    django_capture_on_commit_callbacks,
):
    """
    Test that the task due date is set to task creation date plus the number of
    days specified in the task template.
    """
    template = TaskTemplateFactory(due_in=randint(1, 365))
    with django_capture_on_commit_callbacks(execute=True):
        event = IssueEventFactory(event_type=EventType.PARALEGAL)
        event.save()

    assert Task.objects.count() == 1
    task = Task.objects.first()
    assert task.due_at == (task.created_at + timedelta(days=template.due_in)).date()
