import io
from uuid import uuid4

import factory
from faker import Faker
from django.core.files.uploadedfile import InMemoryUploadedFile
from django.db.models.signals import post_save
from django.utils import timezone

from accounts.models import User
from emails.models import Email, EmailState, EmailAttachment
from core.models import Client, FileUpload, Issue, Person, Tenancy

TINY_PNG = b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x06\x00\x00\x00\x1f\x15\xc4\x89\x00\x00\x00\tpHYs\x00\x00\x0e\xc4\x00\x00\x0e\xc4\x01\x95+\x0e\x1b\x00\x00\x00\x19tEXtSoftware\x00gnome-screenshot\xef\x03\xbf>\x00\x00\x00\rIDAT\x08\x99c```\xf8\x0f\x00\x01\x04\x01\x00}\xb2\xc8\xdf\x00\x00\x00\x00IEND\xaeB`\x82"

fake = Faker()


class UserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = User

    email = factory.Faker("email")
    first_name = factory.Faker("first_name")
    last_name = factory.Faker("last_name")
    date_joined = factory.Faker(
        "date_time_between", tzinfo=timezone.utc, start_date="-2y", end_date="-1y"
    )
    is_staff = False
    is_active = True

    @factory.lazy_attribute
    def username(self):
        return self.email


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
    call_times = ["WEEK_DAY"]


@factory.django.mute_signals(post_save)
class PersonFactory(TimestampedModelFactory):
    class Meta:
        model = Person

    full_name = factory.Faker("name")
    email = factory.Faker("ascii_email")
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
class IssueFactory(TimestampedModelFactory):
    class Meta:
        model = Issue

    id = factory.LazyAttribute(lambda x: uuid4())
    topic = "REPAIRS"
    answers = {}
    client = factory.SubFactory(ClientFactory)
    stage = "UNSTARTED"
    is_sharepoint_set_up = True


@factory.django.mute_signals(post_save)
class FileUploadFactory(TimestampedModelFactory):
    class Meta:
        model = FileUpload

    id = factory.LazyAttribute(lambda x: uuid4())
    issue = factory.SubFactory(IssueFactory)

    @factory.post_generation
    def file(self, create, extracted, **kwargs):
        if extracted:
            file_name, file = extracted
        else:
            file_name = "image.png"
            file = get_dummy_file(file_name)

        self.file.save(file_name, file)


@factory.django.mute_signals(post_save)
class EmailFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Email

    issue = factory.SubFactory(IssueFactory)
    sender = factory.SubFactory(UserFactory)
    subject = factory.Faker("sentence")
    state = "RECEIVED"
    text = factory.Faker("sentence")
    received_data = {}
    created_at = factory.Faker(
        "date_time_between", tzinfo=timezone.utc, start_date="-2m", end_date="-1m"
    )


@factory.django.mute_signals(post_save)
class EmailAttachmentFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = EmailAttachment

    email = factory.SubFactory(EmailFactory)
    content_type = "image/png"
    created_at = factory.Faker(
        "date_time_between", tzinfo=timezone.utc, start_date="-2m", end_date="-1m"
    )

    @factory.post_generation
    def file(self, create, extracted, **kwargs):
        if extracted:
            file_name, file = extracted
        else:
            file_name = "image.png"
            file = get_dummy_file(file_name)

        self.file.save(file_name, file)


def get_dummy_file(name):
    f = io.BytesIO(TINY_PNG)
    return InMemoryUploadedFile(f, None, name, "image/png", len(TINY_PNG), None)
