import factory
from core.factories import TimestampedModelFactory
from django.db.models.signals import post_save
from webhooks.models import WebflowContact


@factory.django.mute_signals(post_save)
class WebflowContactFactory(TimestampedModelFactory):
    class Meta:
        model = WebflowContact

    name = factory.Faker("name")
    email = factory.Faker("email")
    phone = factory.Faker("phone_number")
