import logging
from django.db.models import Q
from utils.sentry import sentry_task

from core.models import Issue, IssueEvent
from core.models.issue_event import EventType
from task.models import TaskTrigger, Task
from task.models.trigger import TriggerTopic

logger = logging.getLogger(__name__)


@sentry_task
def handle_event(event_pk: int):
    event = IssueEvent.objects.get(pk=event_pk)
    maybe_create_tasks(event)


def maybe_create_tasks(event: IssueEvent):
    """
    Look for task triggers matching the event details and create tasks based on
    the templates associated with the trigger.
    """

    # Don't create any tasks if a user has been removed from a case.
    if not is_user_removed(event):
        issue: Issue = event.issue
        query = Q(event=event.event_type, topic__in=[issue.topic, TriggerTopic.ANY])
        if event.event_type == EventType.STAGE:
            query &= Q(event_stage=event.next_stage)

        for trigger in TaskTrigger.objects.filter(query):
            for template in trigger.templates.all():
                Task.objects.get_or_create(
                    role=trigger.tasks_assigned_to,
                    template=template,
                    issue=issue,
                    defaults={
                        "type": template.type,
                        "name": template.name,
                        "description": template.description,
                    },
                )


def is_user_removed(event: IssueEvent) -> bool:
    return is_user_event(event) and not event.next_user_id


def is_user_event(event: IssueEvent) -> bool:
    return event.event_type in [EventType.PARALEGAL, EventType.LAWYER]
