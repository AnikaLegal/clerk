from uuid import uuid4

import factory
from django.db.models.signals import post_save
from django.utils import timezone

from core.models import (
    Client,
    Tenancy,
    FileUpload,
    Submission,
    Person,
    TimestampedModel,
)

from .utils import get_dummy_file


class TimestampedModelFactory(factory.django.DjangoModelFactory):

    modified_at = factory.Faker(
        "date_time_between", tzinfo=timezone.utc, start_date="-1m", end_date="now"
    )
    created_at = factory.Faker(
        "date_time_between", tzinfo=timezone.utc, start_date="-2m", end_date="-1m"
    )


@factory.django.mute_signals(post_save)
class ClientFactory(TimestampedModelFactory):
    class Meta:
        model = Client

    first_name = factory.Faker("first_name")
    last_name = factory.Faker("last_name")
    email = factory.Faker("ascii_email")
    date_of_birth = factory.Faker(
        "date_time_between", tzinfo=timezone.utc, start_date="-50y", end_date="-18y"
    )
    phone_number = factory.Faker("phone_number")
    call_time = "WEEK_DAY"


@factory.django.mute_signals(post_save)
class PersonFactory(TimestampedModelFactory):
    class Meta:
        model = Person

    full_name = factory.Faker("name")
    email = factory.Faker("ascii_email")
    company = factory.Faker("company")
    address = factory.Faker("address")
    phone_number = factory.Faker("phone_number")


@factory.django.mute_signals(post_save)
class TenancyFactory(TimestampedModelFactory):
    class Meta:
        model = Tenancy

    client = factory.SubFactory(ClientFactory)
    agent = factory.SubFactory(PersonFactory)
    landlord = factory.SubFactory(PersonFactory)
    address = factory.Faker("address")
    started = factory.Faker(
        "date_time_between", tzinfo=timezone.utc, start_date="-1y", end_date="-2y"
    )
    is_on_lease = True


@factory.django.mute_signals(post_save)
class SubmissionFactory(TimestampedModelFactory):
    class Meta:
        model = Submission

    id = factory.LazyAttribute(lambda x: uuid4())
    questions = {}
    topic = "REPAIRS"
    client = factory.SubFactory(ClientFactory)


@factory.django.mute_signals(post_save)
class FileUploadFactory(TimestampedModelFactory):
    class Meta:
        model = FileUpload

    id = factory.LazyAttribute(lambda x: uuid4())
    submission = factory.SubFactory(SubmissionFactory)

    @factory.post_generation
    def file(self, create, extracted, **kwargs):
        if extracted:
            file_name, file = extracted
        else:
            file_name = "doc.pdf"
            file = get_dummy_file(file_name)

        self.file.save(file_name, file)
