from uuid import uuid4

import factory
from django.db.models.signals import post_save
from django.utils import timezone

from questions.models import FileUpload, ImageUpload, Submission

from .utils import get_dummy_file


class TimestampedModelFactory(factory.django.DjangoModelFactory):

    modified_at = factory.Faker(
        "date_time_between", tzinfo=timezone.utc, start_date="-1m", end_date="now"
    )
    created_at = factory.Faker(
        "date_time_between", tzinfo=timezone.utc, start_date="-2m", end_date="-1m"
    )


@factory.django.mute_signals(post_save)
class SubmissionFactory(TimestampedModelFactory):
    class Meta:
        model = Submission

    id = factory.LazyAttribute(lambda x: uuid4())
    questions = {}
    answers = {}


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
