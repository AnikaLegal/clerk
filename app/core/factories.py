import io
import os
from datetime import timezone
from unittest.mock import patch
from uuid import uuid4

import factory
from accounts.models import User
from core.models import (
    Client,
    DocumentTemplate,
    FileUpload,
    Issue,
    IssueNote,
    Person,
    Service,
    Tenancy,
)
from core.models.issue import CaseStage, CaseTopic
from core.models.service import DiscreteServiceType, OngoingServiceType, ServiceCategory
from django.core.files.uploadedfile import InMemoryUploadedFile
from django.db.models.signals import post_save
from emails.models import Email, EmailAttachment, EmailTemplate
from faker import Faker
from microsoft.storage import MSGraphStorage
from notify.models import (
    NOTIFY_TOPIC_CHOICES,
    Notification,
    NotifyChannel,
    NotifyEvent,
    NotifyTarget,
)

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
        "date_time_between", tzinfo=timezone.utc, start_date="-1M", end_date="now"
    )
    created_at = factory.Faker(
        "date_time_between", tzinfo=timezone.utc, start_date="-2M", end_date="-1M"
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

    agent = factory.SubFactory(PersonFactory)
    landlord = factory.SubFactory(PersonFactory)
    address = factory.Faker("street_address")
    suburb = factory.Faker("city")
    postcode = factory.Faker("postcode")
    started = factory.Faker(
        "date_time_between", tzinfo=timezone.utc, start_date="-1y", end_date="-2y"
    )
    is_on_lease = "YES"


@factory.django.mute_signals(post_save)
class IssueFactory(TimestampedModelFactory):
    class Meta:
        model = Issue

    id = factory.LazyAttribute(lambda x: uuid4())
    topic = factory.Faker(
        "random_element", elements=[x[0] for x in CaseTopic.ACTIVE_CHOICES]
    )
    answers = {}
    client = factory.SubFactory(ClientFactory)
    tenancy = factory.SubFactory(TenancyFactory)
    stage = "UNSTARTED"
    is_sharepoint_set_up = True


@factory.django.mute_signals(post_save)
class IssueNoteFactory(TimestampedModelFactory):
    class Meta:
        model = IssueNote

    issue = factory.SubFactory(IssueFactory)
    creator = factory.SubFactory(UserFactory)
    note_type = "PARALEGAL"
    text = factory.Faker("sentence")


@factory.django.mute_signals(post_save)
class FileUploadFactory(TimestampedModelFactory):
    class Meta:
        model = FileUpload
        # Suppress test warning.
        skip_postgeneration_save = True

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
        "date_time_between", tzinfo=timezone.utc, start_date="-2M", end_date="now"
    )


@factory.django.mute_signals(post_save)
class EmailTemplateFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = EmailTemplate

    name = factory.Faker("sentence")
    topic = "GENERAL"
    text = factory.Faker("sentence")
    subject = factory.Faker("sentence")


@factory.django.mute_signals(post_save)
class EmailAttachmentFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = EmailAttachment

    email = factory.SubFactory(EmailFactory)
    content_type = "image/png"
    created_at = factory.Faker(
        "date_time_between", tzinfo=timezone.utc, start_date="-2M", end_date="now"
    )


def get_dummy_file(name):
    f = io.BytesIO(TINY_PNG)
    return InMemoryUploadedFile(f, None, name, "image/png", len(TINY_PNG), None)


@factory.django.mute_signals(post_save)
class NotificationFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Notification

    name = factory.Faker("color_name")
    topic = factory.Faker(
        "random_element", elements=[c[0] for c in NOTIFY_TOPIC_CHOICES]
    )
    event = factory.Faker(
        "random_element", elements=[c[0] for c in NotifyEvent.choices]
    )
    channel = factory.Faker(
        "random_element", elements=[c[0] for c in NotifyChannel.choices]
    )
    target = factory.Faker(
        "random_element", elements=[c[0] for c in NotifyTarget.choices]
    )
    event_stage = factory.Faker(
        "random_element", elements=[c[0] for c in CaseStage.CHOICES]
    )
    raw_text = factory.Faker("sentence")
    message_text = factory.Faker("sentence")


@factory.django.mute_signals(post_save)
class ServiceFactory(TimestampedModelFactory):
    class Meta:
        model = Service

    category = factory.Faker("random_element", elements=ServiceCategory)
    type = factory.Maybe(
        factory.LazyAttribute(lambda self: self.category == ServiceCategory.DISCRETE),
        yes_declaration=factory.Faker("random_element", elements=DiscreteServiceType),
        no_declaration=factory.Faker("random_element", elements=OngoingServiceType),
    )
    issue = factory.SubFactory(IssueFactory)
    started_at = factory.Faker("date_between", start_date="-2M", end_date="-1w")
    notes = factory.Faker("paragraph")

    # Yikes!
    # If service is discrete the finished_at always None.
    # If service is ongoing then 50/50 chance of None or date from started_at to now.
    finished_at = factory.Maybe(
        factory.LazyAttribute(lambda self: self.category == ServiceCategory.ONGOING),
        yes_declaration=factory.Maybe(
            factory.LazyFunction(lambda: fake.boolean(chance_of_getting_true=50)),
            yes_declaration=factory.Faker(
                "past_date", start_date=factory.SelfAttribute("..started_at")
            ),
            no_declaration=None,
        ),
        no_declaration=None,
    )
    count = factory.Maybe(
        factory.LazyAttribute(lambda self: self.category == ServiceCategory.DISCRETE),
        yes_declaration=factory.Faker("pyint", min_value=1, max_value=3),
        no_declaration=1,
    )


@factory.django.mute_signals(post_save)
class DocumentTemplateFactory(TimestampedModelFactory):
    class Meta:
        model = DocumentTemplate

    topic = factory.Faker(
        "random_element", elements=[x[0] for x in CaseTopic.ACTIVE_CHOICES]
    )
    file = factory.django.FileField()

    @classmethod
    def _create(cls, model_class, *args, **kwargs):
        template = model_class(*args, **kwargs)
        # Prevent the Django file storage API from using the MS Graph API as it
        # does not work in tests. This is a convenience as we could do this in
        # the tests themselves but that would be tedious.
        with patch.object(MSGraphStorage, "exists", return_value=False):
            name = DocumentTemplate._get_upload_to(template, template.file.name)
            with patch.object(MSGraphStorage, "_save", return_value=name):
                template.save()

        # We have a custom annotation tied to the default manager that we want
        # to access in tests.
        return model_class.objects.get(pk=template.pk)
