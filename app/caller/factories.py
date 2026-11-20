import factory

from caller.models import Call
from core.factories import TimestampedModelFactory
from core.models.issue import CaseTopic


class CallFactory(TimestampedModelFactory):
    class Meta:
        model = Call

    phone_number = factory.Faker("numerify", text="+614########")
    topic = factory.Iterator([value for value, _ in CaseTopic.CHOICES])

