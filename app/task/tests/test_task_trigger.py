import pytest

from core.factories import IssueEventFactory
from core.models.issue_event import EventType
from task.factories import TaskTriggerFactory, TaskTemplateFactory
from task.models import Task


@pytest.mark.django_db
@pytest.mark.enable_signals
def test_task_trigger__tasks_created_when_issue_created(
    django_capture_on_commit_callbacks,
):
    """
    Test task trigger activates and tasks are created when an issue is created.
    """
    trigger = TaskTriggerFactory(event=EventType.CREATE)
    TaskTemplateFactory(trigger=trigger)
    TaskTemplateFactory(trigger=trigger)

    with django_capture_on_commit_callbacks(execute=True):
        event = IssueEventFactory(event_type=EventType.CREATE)
        event.save()

    assert Task.objects.filter(issue=event.issue).count() == 2
