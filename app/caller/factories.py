import factory

from caller.models import Call, Callback
from core.factories import TimestampedModelFactory
from core.models.issue import CaseTopic


class CallFactory(TimestampedModelFactory):
    class Meta:
        model = Call

    phone_number = factory.Faker("numerify", text="+614########")
    topic = factory.Iterator([value for value, _ in CaseTopic.CHOICES])


class CallbackFactory(TimestampedModelFactory):
    class Meta:
        model = Callback

    call = factory.SubFactory(CallFactory)
    is_answered = True
    purpose = factory.Faker("sentence")
    summary = factory.Faker("sentence")
