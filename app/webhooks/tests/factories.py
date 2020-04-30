from uuid import uuid4

import factory
from django.db.models.signals import post_save
from django.utils import timezone

from questions.tests.factories import TimestampedModelFactory
from webhooks.models import WebflowContact


class TimestampedModelFactory(factory.django.DjangoModelFactory):

    modified_at = factory.Faker(
        "date_time_between", tzinfo=timezone.utc, start_date="-1m", end_date="now"
    )
    created_at = factory.Faker(
        "date_time_between", tzinfo=timezone.utc, start_date="-2m", end_date="-1m"
    )


@factory.django.mute_signals(post_save)
class WebflowContactFactory(TimestampedModelFactory):
    class Meta:
        model = WebflowContact

    name = factory.Faker("name")
    email = factory.Faker("ascii_email")
    phone = factory.Faker("phone_number")
