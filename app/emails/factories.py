import io
from random import randint

import factory
from django.core.files.uploadedfile import InMemoryUploadedFile
from emails.models import (
    ReceivedAttachment,
    ReceivedEmail,
)
from faker import Faker

fake = Faker()


class ReceivedEmailFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = ReceivedEmail
        skip_postgeneration_save = True

    received_data = factory.Dict(
        {
            "subject": factory.Faker("sentence"),
            "envelope": factory.Dict(
                {
                    "to": [fake.email()],
                    "from": fake.email(),
                }
            ),
            "to": factory.Faker("email"),
            "text": factory.Faker("text"),
            "html": f"<b>{fake.text()}</b>",
        }
    )

    attachments = factory.RelatedFactoryList(
        "emails.factories.ReceivedAttachmentFactory",
        "email",
        size=lambda: randint(1, 5),
    )


class ReceivedAttachmentFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = ReceivedAttachment

    email = factory.SubFactory(ReceivedEmailFactory)
    name = factory.Sequence(lambda n: f"file_{n}.pdf")
    content_type = "application/pdf"

    @factory.lazy_attribute
    def file(self):
        bytes = io.BytesIO(fake.text().encode())
        bytes.seek(0)  # Reset pointer to the beginning of the file
        return InMemoryUploadedFile(
            bytes,
            field_name="file",
            name=self.name,
            content_type=self.content_type,
            size=len(bytes.getvalue()),
            charset=None,
        )
