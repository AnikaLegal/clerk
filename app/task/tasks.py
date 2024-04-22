import logging
from django.db.models import Q
from utils.sentry import sentry_task

from core.models.issue_event import IssueEvent, EventType
from task.models.trigger import TaskTrigger


logger = logging.getLogger(__name__)


@sentry_task
def create_tasks(issue_event_pk: int):
    """
    TODO: describe function.
    """
    try:
        event = IssueEvent.objects.get(pk=issue_event_pk)
    except IssueEvent.DoesNotExist:
        # TODO: log as this shouldn't happen.
        return

    query = Q(event=event.event_type) & Q(topic__in=[event.issue.topic, "ANY"])
    if event.event_type == EventType.STAGE:
        query &= Q(event_stage=event.next_stage)

    triggers = TaskTrigger.objects.filter(query)
    for trigger in triggers:
        pass
