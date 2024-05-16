import pytest

from core.factories import IssueFactory
from core.models.issue_event import EventType
from task.factories import TaskTriggerFactory, TaskTemplateFactory
from task.models import Task

"""
Changes required to core factories to support testing task creation easily:

    index 8bcf553..b87da65 100644
    --- a/app/core/factories.py
    +++ b/app/core/factories.py
    @@ -91,7 +91,6 @@ class TenancyFactory(TimestampedModelFactory):
        is_on_lease = "YES"
    
    
    -@factory.django.mute_signals(post_save)
    class IssueFactory(TimestampedModelFactory):
        class Meta:
            model = Issue

We need to remove the muting of post_save signals.
"""
@pytest.mark.skip(reason="requires changes to core factories")
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
        IssueFactory()

    assert Task.objects.count() == 2
