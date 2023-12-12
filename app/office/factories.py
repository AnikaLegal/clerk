import io
from sys import getsizeof
import factory
from django.core.files.uploadedfile import InMemoryUploadedFile
from django.db.models.signals import post_save
from django.utils import timezone

from office.models import Closure, ClosureTemplate

TINY_WAV = b"RIFF$\x00\x00\x00WAVEfmt \x10\x00\x00\x00\x01\x00\x01\x00D\xac\x00\x00\x88X\x01\x00\x02\x00\x10\x00data\x00\x00\x00\x00"


def _get_call_audio_file():
    f = io.BytesIO(TINY_WAV)
    return InMemoryUploadedFile(
        f, None, "call_audio.wav", "audio/wav", getsizeof(f), None
    )


class ClosureTemplateFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = ClosureTemplate

    created_at = factory.Faker(
        "date_time_between", tzinfo=timezone.utc, start_date="-2m", end_date="-1m"
    )
    call_text = "call text"
    email_html = "email text"
    notice_html = "notice html"


class ClosureFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Closure

    created_at = factory.Faker(
        "date_time_between", tzinfo=timezone.utc, start_date="-2m", end_date="-1m"
    )
    close_date = factory.Faker(
        "date_between", start_date="-2w", end_date="-1w"
    )
    reopen_date = factory.Faker(
        "date_between", start_date="+1w", end_date="+2w"
    )
    # call_audio = factory.django.FileField(from_func=_get_call_audio_file)
    template = factory.SubFactory(ClosureTemplateFactory)
