import logging
from django.db.models import Q
from utils.sentry import sentry_task

from accounts.models import User
from core.models import Issue, IssueEvent
from core.models.issue_event import EventType
from task.models import TaskTrigger, Task
from task.models.trigger import TriggerTopic, TasksCaseRole

logger = logging.getLogger(__name__)


@sentry_task
def maybe_create_tasks(event_pk: int):
    """
    Look for task triggers matching the issue event details and create tasks
    based on the templates associated with the trigger.
    """
    try:
        event = IssueEvent.objects.get(pk=event_pk)
    except IssueEvent.DoesNotExist:
        return

    issue = event.issue
    query = Q(event=event.event_type, topic__in=[issue.topic, TriggerTopic.ANY])
    if event.event_type == EventType.STAGE:
        query &= Q(event_stage=event.next_stage)

    for trigger in TaskTrigger.objects.filter(query):
        role = trigger.tasks_assigned_to
        user = get_case_user_by_role(issue, role)

        for template in trigger.templates.all():
            if not Task.objects.filter(template=template, issue=issue).exists():
                Task.objects.create(
                    template=template,
                    issue=issue,
                    type=template.type,
                    name=template.name,
                    description=template.description,
                    assigned_to=user,
                )


def get_case_user_by_role(issue: Issue, role: TasksCaseRole) -> User:
    if role == TasksCaseRole.PARALEGAL:
        return issue.paralegal
    if role == TasksCaseRole.LAWYER:
        return issue.lawyer
    if role == TasksCaseRole.COORDINATOR:
        # TODO: this is yuk. Do better.
        return User.objects.get(email="coordinators@anikalegal.com")
    return None
