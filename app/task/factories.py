import factory
from faker import Faker
from django.db.models.signals import post_save

from core.factories import TimestampedModelFactory
from core.models.issue_event import EventType
from task.models import TaskTrigger, TaskTemplate
from task.models.trigger import TriggerTopic, TasksCaseRole
from task.models.template import TaskType


fake = Faker()


class TaskTriggerFactory(TimestampedModelFactory):
    class Meta:
        model = TaskTrigger

    topic = TriggerTopic.ANY
    event = EventType.PARALEGAL
    tasks_assignment_role = TasksCaseRole.PARALEGAL


class TaskTemplateFactory(TimestampedModelFactory):
    class Meta:
        model = TaskTemplate

    type = factory.Faker("random_element", elements=[c[0] for c in TaskType.choices])
    name = factory.Faker("sentence")
    description = factory.Faker("paragraph")
    trigger = factory.SubFactory(TaskTriggerFactory)
