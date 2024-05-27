import pytest
from unittest import mock
from random import randint

from core.factories import IssueEventFactory, IssueFactory, UserFactory
from core.models.issue import CaseStage
from core.models.issue_event import EventType
from task.factories import TaskTriggerFactory, TaskTemplateFactory, TaskFactory
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
    templates = TaskTemplateFactory.create_batch(randint(1, 3), trigger=trigger)

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
    templates = TaskTemplateFactory.create_batch(randint(1, 3), trigger=trigger)

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


# TODO: add tests for
# - suspended tasks
# - reassigned tasks
# - resumed tasks


@pytest.mark.django_db
@pytest.mark.enable_signals
def test_task_trigger__one_task_reverts_to_owner(
    django_capture_on_commit_callbacks,
):
    """
    Test the behaviour where a user is removed from a case and they have an
    assigned task and they are not the owner of that task. The task should be
    assigned back (reverted) to the owner.
    """
    user_1 = UserFactory()
    user_2 = UserFactory()
    issue = IssueFactory()
    tasks = TaskFactory.create_batch(
        randint(1, 3), issue=issue, assigned_to=user_1, owner=user_2
    )

    with django_capture_on_commit_callbacks(execute=True):
        event = IssueEventFactory(
            issue=issue,
            event_type=EventType.PARALEGAL,
            prev_user=user_1,
            next_user=None,
        )
        event.save()

    assert Task.objects.filter(
        issue=issue, assigned_to=user_2, owner=user_2
    ).count() == len(tasks)


@pytest.mark.django_db
@pytest.mark.enable_signals
def test_task_trigger__tasks_revert_to_owner(
    django_capture_on_commit_callbacks,
):
    """
    Test the behaviour where a user is removed from a case and they have
    assigned tasks and they are not the owner of those tasks. The tasks should
    be assigned back (reverted) to the owner. Tasks assigned to the same user
    but related to different issues should be unaffected. Tasks assigned to a
    different user & related to a different issue should be unaffected.
    """
    user_1 = UserFactory()
    user_2 = UserFactory()
    user_3 = UserFactory()

    issue_1 = IssueFactory()
    issue_2 = IssueFactory()
    issue_3 = IssueFactory()

    tasks_1 = TaskFactory.create_batch(
        randint(1, 3), issue=issue_1, assigned_to=user_1, owner=user_2
    )
    # Different issue but same assignee & owner as tasks above.
    tasks_2 = TaskFactory.create_batch(
        randint(1, 3), issue=issue_2, assigned_to=user_1, owner=user_2
    )
    # Different issue, assignee & owner.
    tasks_3 = TaskFactory.create_batch(
        randint(1, 3), issue=issue_3, assigned_to=user_3, owner=user_3
    )

    with django_capture_on_commit_callbacks(execute=True):
        event = IssueEventFactory(
            issue=issue_1,
            event_type=EventType.PARALEGAL,
            prev_user=user_1,
            next_user=None,
        )
        event.save()

    # Tasks belonging to the issue related to the event have been reverted to
    # the owner?
    assert Task.objects.filter(
        issue=issue_1, assigned_to=user_2, owner=user_2
    ).count() == len(tasks_1)

    # Tasks belonging to a different issue but with the same users are unchanged.
    assert Task.objects.filter(
        issue=issue_2, assigned_to=user_1, owner=user_2
    ).count() == len(tasks_2)

    # Tasks belonging to a different issue, assignee & owner are unchanged.
    assert Task.objects.filter(
        issue=issue_3, assigned_to=user_3, owner=user_3
    ).count() == len(tasks_3)