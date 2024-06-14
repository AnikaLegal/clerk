import factory
from django.utils import timezone
from office.models import Closure, ClosureTemplate


class ClosureTemplateFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = ClosureTemplate

    created_at = factory.Faker(
        "date_time_between", tzinfo=timezone.utc, start_date="-2M", end_date="-1M"
    )
    call_text = factory.Faker("text")
    email_html = factory.Faker("text")
    notice_html = factory.Faker("text")


class ClosureFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Closure

    created_at = factory.Faker(
        "date_time_between", tzinfo=timezone.utc, start_date="-2M", end_date="-1M"
    )
    close_date = factory.Faker("date_between", start_date="-2w", end_date="-1w")
    reopen_date = factory.Faker("date_between", start_date="+1w", end_date="+2w")
    template = factory.SubFactory(ClosureTemplateFactory)
