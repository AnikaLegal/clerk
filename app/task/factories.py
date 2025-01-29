from datetime import timezone
from random import randint

import factory
from core.factories import IssueFactory, TimestampedModelFactory, UserFactory
from core.models.issue_event import EventType
from faker import Faker
from task.models import Task, TaskTemplate, TaskTrigger
from task.models.task import TaskStatus
from task.models.template import TaskTemplateType
from task.models.trigger import TasksCaseRole, TriggerTopic

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

    type = factory.Faker("random_element", elements=[c[0] for c in TaskTemplateType.choices])
    name = factory.Faker("text", max_nb_chars=45)
    description = factory.Faker("paragraph")
    trigger = factory.SubFactory(TaskTriggerFactory, templates=[])
    due_in = factory.Maybe(
        factory.LazyFunction(lambda: fake.boolean(chance_of_getting_true=50)),
        yes_declaration=factory.Faker("pyint", min_value=1, max_value=28),
        no_declaration=None,
    )
    is_urgent = factory.Faker("random_element", elements=[True, False])
    is_approval_required = factory.Faker("random_element", elements=[True, False])


class TaskFactory(TimestampedModelFactory):
    class Meta:
        model = Task

    type = factory.Faker("random_element", elements=[c[0] for c in TaskTemplateType.choices])
    name = factory.Faker("text", max_nb_chars=45)
    description = "\n\n".join(
        [fake.text(max_nb_chars=randint(100, 200)) for _ in range(randint(2, 5))]
    )
    status = factory.Faker(
        "random_element", elements=[c[0] for c in TaskStatus.choices]
    )
    assigned_to = factory.SubFactory(UserFactory)
    assignee_role = TasksCaseRole.PARALEGAL
    issue = factory.SubFactory(
        IssueFactory,
        paralegal=factory.SelfAttribute("..assigned_to"),
        lawyer=factory.SubFactory(UserFactory),
        is_alert_sent=True,
        is_welcome_email_sent=True,
    )
    created_at = factory.Faker(
        "date_time_between", tzinfo=timezone.utc, start_date="-2M"
    )
    due_at = factory.Maybe(
        factory.LazyFunction(lambda: fake.boolean(chance_of_getting_true=50)),
        yes_declaration=factory.Faker(
            "date_between",
            start_date="-1w",
            end_date="+2w",
        ),
        no_declaration=None,
    )

    is_urgent = factory.Faker("boolean", chance_of_getting_true=10)
    is_approval_required = factory.Faker("boolean", chance_of_getting_true=20)
    is_open = factory.LazyAttribute(
        lambda self: self.status not in [TaskStatus.DONE, TaskStatus.NOT_DONE]
    )
    closed_at = factory.Maybe(
        "is_open",
        yes_declaration=None,
        no_declaration=factory.Faker(
            "past_datetime",
            start_date=factory.SelfAttribute("..created_at"),
            tzinfo=timezone.utc,
        ),
    )
