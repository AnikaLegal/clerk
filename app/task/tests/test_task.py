import pytest
from random import randint

from core.factories import IssueEventFactory, IssueFactory, UserFactory
from core.models.issue_event import EventType
from task.factories import TaskFactory
from task.models import Task
from task.models.task import OwnerRole, TaskStatus


@pytest.mark.django_db
@pytest.mark.enable_signals
def test_task__tasks_reverted(
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
    user_4 = UserFactory()

    issue_1 = IssueFactory()
    issue_2 = IssueFactory()
    issue_3 = IssueFactory()

    # Tasks that should be reverted as they are assigned to user removed from
    # case.
    tasks_1 = TaskFactory.create_batch(
        randint(1, 3),
        status=TaskStatus.NOT_STARTED,
        issue=issue_1,
        assigned_to=user_1,
        owner=user_2,
    )
    # Same issue but different assignee as tasks to be reverted.
    tasks_2 = TaskFactory.create_batch(
        randint(1, 3),
        status=TaskStatus.NOT_STARTED,
        issue=issue_1,
        assigned_to=user_3,
        owner=user_2,
    )
    # Different issue but same assignee & owner as tasks to be reverted.
    tasks_3 = TaskFactory.create_batch(
        randint(1, 3),
        status=TaskStatus.NOT_STARTED,
        issue=issue_2,
        assigned_to=user_1,
        owner=user_2,
    )
    # Different issue, assignee & owner as tasks to be reverted.
    tasks_4 = TaskFactory.create_batch(
        randint(1, 3),
        status=TaskStatus.NOT_STARTED,
        issue=issue_3,
        assigned_to=user_4,
        owner=user_4,
    )

    with django_capture_on_commit_callbacks(execute=True):
        event = IssueEventFactory(
            issue=issue_1,
            event_type=EventType.PARALEGAL,
            prev_user=user_1,
            next_user=None,
        )
        event.save()

    # There are no tasks related to the event issue and assigned to the user
    # that was removed from the case?
    assert (
        Task.objects.filter(issue=issue_1, assigned_to=user_1, owner=user_2).count()
        == 0
    )
    # Tasks related to the event issue that were assigned to the user removed
    # from the case have now been assigned to the task owner?
    assert Task.objects.filter(
        issue=issue_1, assigned_to=user_2, owner=user_2, pk__in=[t.pk for t in tasks_1]
    ).count() == len(tasks_1)

    # Tasks belonging to the same issue and same owner but a different assignee
    # are unchanged?
    assert Task.objects.filter(
        issue=issue_1, assigned_to=user_3, owner=user_2, pk__in=[t.pk for t in tasks_2]
    ).count() == len(tasks_2)

    # Tasks belonging to a different issue but with the same users are unchanged?
    assert Task.objects.filter(
        issue=issue_2, assigned_to=user_1, owner=user_2, pk__in=[t.pk for t in tasks_3]
    ).count() == len(tasks_3)

    # Tasks belonging to a different issue, assignee & owner are unchanged?
    assert Task.objects.filter(
        issue=issue_3, assigned_to=user_4, owner=user_4, pk__in=[t.pk for t in tasks_4]
    ).count() == len(tasks_4)


@pytest.mark.django_db
@pytest.mark.enable_signals
def test_task__tasks_suspended(
    django_capture_on_commit_callbacks,
):
    """
    Test the behaviour where a user is removed from a case and they are the
    owner of a number of tasks. Those tasks should be suspended.
    """
    user_1 = UserFactory()
    user_2 = UserFactory()
    user_3 = UserFactory()

    issue_1 = IssueFactory()
    issue_2 = IssueFactory()
    issue_3 = IssueFactory()

    # Tasks that should be suspended.
    tasks_1 = TaskFactory.create_batch(
        randint(1, 3),
        status=TaskStatus.NOT_STARTED,
        issue=issue_1,
        assigned_to=user_1,
        owner=user_1,
    )
    # Same issue but different assignee & owner as tasks to be suspended.
    tasks_2 = TaskFactory.create_batch(
        randint(1, 3),
        status=TaskStatus.NOT_STARTED,
        issue=issue_1,
        assigned_to=user_2,
        owner=user_2,
    )
    # Different issue but same assignee & owner as tasks to be suspended.
    tasks_3 = TaskFactory.create_batch(
        randint(1, 3),
        status=TaskStatus.NOT_STARTED,
        issue=issue_2,
        assigned_to=user_1,
        owner=user_1,
    )
    # Different issue, assignee & owner as tasks to be suspended.
    tasks_4 = TaskFactory.create_batch(
        randint(1, 3),
        status=TaskStatus.NOT_STARTED,
        issue=issue_3,
        assigned_to=user_3,
        owner=user_3,
    )

    with django_capture_on_commit_callbacks(execute=True):
        event = IssueEventFactory(
            issue=issue_1,
            event_type=EventType.PARALEGAL,
            prev_user=user_1,
            next_user=None,
        )
        event.save()

    # There are no tasks related to the event issue and assigned to the user
    # that was removed from the case?
    assert (
        Task.objects.filter(issue=issue_1, assigned_to=user_1, owner=user_1).count()
        == 0
    )
    # Tasks related to the event issue that were assigned to the user removed
    # from the case have now been suspended?
    assert Task.objects.filter(
        issue=issue_1,
        assigned_to__isnull=True,
        owner__isnull=True,
        is_suspended=True,
        prev_owner_role=EventType.PARALEGAL,
        pk__in=[t.pk for t in tasks_1],
    ).count() == len(tasks_1)

    # Tasks belonging to the same issue but different assignee & owner are
    # unchanged?
    assert Task.objects.filter(
        issue=issue_1, assigned_to=user_2, owner=user_2, pk__in=[t.pk for t in tasks_2]
    ).count() == len(tasks_2)

    # Tasks belonging to a different issue but with the same users are unchanged.
    assert Task.objects.filter(
        issue=issue_2, assigned_to=user_1, owner=user_1, pk__in=[t.pk for t in tasks_3]
    ).count() == len(tasks_3)

    # Tasks belonging to a different issue, assignee & owner are unchanged.
    assert Task.objects.filter(
        issue=issue_3, assigned_to=user_3, owner=user_3, pk__in=[t.pk for t in tasks_4]
    ).count() == len(tasks_4)


@pytest.mark.django_db
@pytest.mark.enable_signals
def test_task__tasks_resumed(
    django_capture_on_commit_callbacks,
):
    """
    Test the behaviour where a user is added to a case that has a number of
    associated but suspended tasks. Only those tasks that match the users role
    should be resumed and assigned to the user.
    """
    next_user = UserFactory()
    other_user = UserFactory()

    issue = IssueFactory()

    # Suspended tasks that should be resumed.
    tasks_1 = TaskFactory.create_batch(
        randint(1, 3),
        issue=issue,
        assigned_to=None,
        owner=None,
        prev_owner_role=OwnerRole.PARALEGAL,
    )
    # Suspended tasks related to the same issue that should not be resumed
    # because the have a different previous owner role.
    tasks_2 = TaskFactory.create_batch(
        randint(1, 3),
        issue=issue,
        assigned_to=None,
        owner=None,
        prev_owner_role=OwnerRole.LAWYER,
    )
    # Active (i.e. not suspended) tasks related to the same issue and currently assigned
    # to the user that will ultimately own the resumed tasks.
    tasks_3 = TaskFactory.create_batch(
        randint(1, 3), issue=issue, assigned_to=next_user, owner=next_user
    )
    # Active (i.e. not suspended) tasks related to the same issue and assigned
    # to a different user.
    tasks_4 = TaskFactory.create_batch(
        randint(1, 3), issue=issue, assigned_to=other_user, owner=other_user
    )

    # Make sure the system thinks the tasks we have created are suspended.
    assert Task.objects.filter(
        issue=issue,
        prev_owner_role=OwnerRole.PARALEGAL,
        pk__in=[t.pk for t in tasks_1],
        is_suspended=True,
    ).count() == len(tasks_1)

    assert Task.objects.filter(
        issue=issue,
        prev_owner_role=OwnerRole.LAWYER,
        pk__in=[t.pk for t in tasks_2],
        is_suspended=True,
    ).count() == len(tasks_2)

    with django_capture_on_commit_callbacks(execute=True):
        event = IssueEventFactory(
            issue=issue,
            event_type=EventType.PARALEGAL,
            prev_user=None,
            next_user=next_user,
        )
        event.save()

    # There are no suspended tasks previously owned by the paralegal related to
    # the event issue.
    assert (
        Task.objects.filter(
            issue=issue, is_suspended=True, prev_owner_role=OwnerRole.PARALEGAL
        ).count()
        == 0
    )
    # Tasks related to the event issue that were suspended have been resumed and
    # assigned to the next user?
    assert Task.objects.filter(
        issue=issue,
        assigned_to=next_user,
        owner=next_user,
        is_suspended=False,
        pk__in=[t.pk for t in tasks_1],
    ).count() == len(tasks_1)

    # The suspended tasks previously owned by the lawyer role are unchanged?
    assert Task.objects.filter(
        issue=issue,
        is_suspended=True,
        prev_owner_role=OwnerRole.LAWYER,
        pk__in=[t.pk for t in tasks_2],
    ).count() == len(tasks_2)

    # Active tasks related to the event issue and previously owned by the next
    # user are unchanged? NOTE: This seems like an unlikely scenario.
    assert Task.objects.filter(
        issue=issue,
        assigned_to=next_user,
        owner=next_user,
        pk__in=[t.pk for t in tasks_3],
    ).count() == len(tasks_3)

    # Active tasks related to the event issue and owned by another user are unchanged.
    assert Task.objects.filter(
        issue=issue,
        assigned_to=other_user,
        owner=other_user,
        pk__in=[t.pk for t in tasks_4],
    ).count() == len(tasks_4)


@pytest.mark.django_db
@pytest.mark.enable_signals
def test_task__tasks_reassigned(
    django_capture_on_commit_callbacks,
):
    """
    Test the behaviour where the user assigned to a case is changed and they are
    the owner of a number fo tasks. Those tasks should be reassigned to the next
    user.
    """
    prev_user = UserFactory()
    next_user = UserFactory()
    other_user = UserFactory()

    issue_1 = IssueFactory()
    issue_2 = IssueFactory()
    issue_3 = IssueFactory()

    # Tasks that should be reassigned.
    tasks_1 = TaskFactory.create_batch(
        randint(1, 3),
        status=TaskStatus.NOT_STARTED,
        issue=issue_1,
        assigned_to=prev_user,
        owner=prev_user,
    )
    # Same issue but different assignee & owner as tasks to be reassigned.
    tasks_2 = TaskFactory.create_batch(
        randint(1, 3),
        status=TaskStatus.NOT_STARTED,
        issue=issue_1,
        assigned_to=other_user,
        owner=other_user,
    )
    # Different issue but same assignee & owner as tasks to be reassigned.
    tasks_3 = TaskFactory.create_batch(
        randint(1, 3),
        status=TaskStatus.NOT_STARTED,
        issue=issue_2,
        assigned_to=prev_user,
        owner=prev_user,
    )
    # Different issue, assignee & owner as tasks to be reassigned.
    tasks_4 = TaskFactory.create_batch(
        randint(1, 3),
        status=TaskStatus.NOT_STARTED,
        issue=issue_3,
        assigned_to=other_user,
        owner=other_user,
    )

    with django_capture_on_commit_callbacks(execute=True):
        event = IssueEventFactory(
            issue=issue_1,
            event_type=EventType.PARALEGAL,
            prev_user=prev_user,
            next_user=next_user,
        )
        event.save()

    # There are no tasks related to the event issue and assigned to the user
    # that was changed?
    assert (
        Task.objects.filter(
            issue=issue_1, assigned_to=prev_user, owner=prev_user
        ).count()
        == 0
    )
    # Tasks related to the event issue that were assigned to the user that was
    # changed have now been reassigned?
    assert Task.objects.filter(
        issue=issue_1,
        assigned_to=next_user,
        owner=next_user,
        pk__in=[t.pk for t in tasks_1],
    ).count() == len(tasks_1)

    # Tasks related to the same issue but different assignee & owner are
    # unchanged?
    assert Task.objects.filter(
        issue=issue_1,
        assigned_to=other_user,
        owner=other_user,
        pk__in=[t.pk for t in tasks_2],
    ).count() == len(tasks_2)

    # Tasks related to a different issue but with the same user are unchanged.
    assert Task.objects.filter(
        issue=issue_2,
        assigned_to=prev_user,
        owner=prev_user,
        pk__in=[t.pk for t in tasks_3],
    ).count() == len(tasks_3)

    # Tasks related to a different issue, assignee & owner are unchanged.
    assert Task.objects.filter(
        issue=issue_3,
        assigned_to=other_user,
        owner=other_user,
        pk__in=[t.pk for t in tasks_4],
    ).count() == len(tasks_4)