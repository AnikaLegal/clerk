import logging
from django.db.models import Q
from utils.sentry import sentry_task

from accounts.models import User
from core.models import Issue
from core.models.issue_event import IssueEvent, EventType
from task.models import TaskTrigger, TaskTemplate, Task
from task.models.trigger import TriggerTopic, TasksAssignedTo


logger = logging.getLogger(__name__)


@sentry_task
def maybe_create_or_update_tasks(issue_event_pk: int):
    """
    Look for task triggers matching the issue event details and create tasks
    based on the templates associated with the trigger.
    """
    try:
        event = IssueEvent.objects.get(pk=issue_event_pk)
    except IssueEvent.DoesNotExist:
        return

    # TODO: handle events where e.g. paralegal removed.
    if event.event_type == EventType.PARALEGAL or event.event_type == EventType.LAWYER:
        if event.prev_user_id and event.next_user_id:
            pass

    issue = event.issue
    query = Q(event=event.event_type, topic__in=[issue.topic, TriggerTopic.ANY])
    if event.event_type == EventType.STAGE:
        query &= Q(event_stage=event.next_stage)

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
