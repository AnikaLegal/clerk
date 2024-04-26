import logging
from django.db.models import Q
from utils.sentry import sentry_task

from core.models.issue_event import IssueEvent, EventType
from task.models import TaskTrigger, Task
from task.models.trigger import TaskTriggerTopic


logger = logging.getLogger(__name__)


@sentry_task
def create_tasks(issue_event_pk: int):
    """
    Look for task triggers matching the issue event details and create tasks
    based on the templates associated with the trigger.
    """
    try:
        event = IssueEvent.objects.get(pk=issue_event_pk)
    except IssueEvent.DoesNotExist:
        return

    issue = event.issue
    query = Q(event=event.event_type, topic__in=[issue.topic, TaskTriggerTopic.ANY])
    if event.event_type == EventType.STAGE:
        query &= Q(event_stage=event.next_stage)

    # TODO: notifications

    for trigger in TaskTrigger.objects.filter(query):
        for template in trigger.templates.all():
            if not Task.objects.filter(template=template, issue=issue).exists():
                Task.objects.create(
                    template=template,
                    issue=issue,
                    type=template.type,
                    name=template.name,
                    description=template.description,
                )
