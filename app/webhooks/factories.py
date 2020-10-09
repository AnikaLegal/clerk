from uuid import uuid4

import factory
from django.db.models.signals import post_save
from django.utils import timezone

from core.factories import TimestampedModelFactory
from webhooks.models import WebflowContact


@factory.django.mute_signals(post_save)
class WebflowContactFactory(TimestampedModelFactory):
    class Meta:
        model = WebflowContact

    name = factory.Faker("name")
    email = factory.Faker("ascii_email")
    phone = factory.Faker("phone_number")
