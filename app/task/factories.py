import factory
from faker import Faker
from random import randint

from core.factories import TimestampedModelFactory, IssueFactory, UserFactory
from core.models.issue_event import EventType
from task.models import TaskTrigger, TaskTemplate, Task
from task.models.trigger import TriggerTopic, TasksCaseRole
from task.models.template import TaskType
from task.models.task import TaskStatus


fake = Faker()


class TaskTriggerFactory(TimestampedModelFactory):
    class Meta:
        model = TaskTrigger
        skip_postgeneration_save = True

    topic = TriggerTopic.ANY
    event = EventType.PARALEGAL
    tasks_assignment_role = TasksCaseRole.PARALEGAL
    templates = factory.RelatedFactoryList(
        "task.factories.TaskTemplateFactory", "trigger", size=lambda: randint(1, 5)
    )


class TaskTemplateFactory(TimestampedModelFactory):
    class Meta:
        model = TaskTemplate

    type = factory.Faker("random_element", elements=[c[0] for c in TaskType.choices])
    name = factory.Faker("text", max_nb_chars=45)
    description = factory.Faker("paragraph")
    trigger = factory.SubFactory(TaskTriggerFactory)


class TaskFactory(TimestampedModelFactory):
    class Meta:
        model = Task

    type = factory.Faker("random_element", elements=[c[0] for c in TaskType.choices])
    name = factory.Faker("text", max_nb_chars=45)
    description = factory.Faker("paragraph")
    status = TaskStatus.NOT_STARTED
    issue = factory.SubFactory(IssueFactory)
    owner = factory.SubFactory(UserFactory)
    assigned_to = factory.SelfAttribute("owner")
