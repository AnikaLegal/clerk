import json

import factory
from django.core.files.uploadedfile import SimpleUploadedFile
from faker import Faker

from web.models import (
    BlogListPage,
    BlogPage,
    CustomDocument,
    DocumentLog,
    Report,
    RootPage,
)
from web.models.document import ReferrerChoices, SectorChoices, StateChoices

fake = Faker()


class BlogListPageFactory(factory.django.DjangoModelFactory[BlogListPage]):
    class Meta:  # pyright: ignore[reportIncompatibleVariableOverride]
        model = BlogListPage

    title = factory.Faker("sentence")
    slug = factory.Faker("slug")

    @classmethod
    def _create(cls, model_class, *args, **kwargs):
        # Get the root page to add child to
        root_page = RootPage.objects.get()
        instance = model_class(*args, **kwargs)
        root_page.add_child(instance=instance)
        instance.save_revision().publish()
        return instance


class BlogPageFactory(factory.django.DjangoModelFactory[BlogPage]):
    class Meta:  # pyright: ignore[reportIncompatibleVariableOverride]
        model = BlogPage

    title = factory.Faker("sentence")
    body = factory.LazyFunction(
        lambda: json.dumps([{"type": "paragraph", "value": fake.paragraph()}])
    )

    @classmethod
    def _create(cls, model_class, parent=None, *args, **kwargs):
        # If no parent provided, create a BlogListPage as parent
        if parent is None:
            parent = BlogListPageFactory()

        instance = model_class(*args, **kwargs)
        parent.add_child(instance=instance)
        instance.save_revision().publish()

        return instance


class DocumentFactory(factory.django.DjangoModelFactory[CustomDocument]):
    class Meta:  # pyright: ignore[reportIncompatibleVariableOverride]
        model = CustomDocument

    file = factory.django.FileField(
        from_file=SimpleUploadedFile(
            name=fake.file_name(),
            content=fake.paragraph().encode(),
            content_type=fake.mime_type(),
        )
    )
    title = factory.Faker("sentence")
    track_download = False


class DocumentLogFactory(factory.django.DjangoModelFactory[DocumentLog]):
    class Meta:  # pyright: ignore[reportIncompatibleVariableOverride]
        model = DocumentLog

    document = factory.SubFactory(DocumentFactory)
    state = factory.Faker(
        "random_element", elements=[c[0] for c in StateChoices.choices]
    )
    sector = factory.Faker(
        "random_element", elements=[c[0] for c in SectorChoices.choices]
    )
    referrer = factory.Faker(
        "random_element", elements=[c[0] for c in ReferrerChoices.choices]
    )
    ip_address = factory.Faker("ipv4")


class ReportFactory(factory.django.DjangoModelFactory[Report]):
    class Meta:  # pyright: ignore[reportIncompatibleVariableOverride]
        model = Report

    class Params:
        is_document = factory.Faker("boolean", chance_of_getting_true=50)

    title = factory.Faker("sentence")
    description = factory.Faker("paragraph")
    is_featured = False
    live = True

    document = factory.LazyAttribute(
        lambda obj: DocumentFactory() if obj.is_document else None
    )
    accessible_document = factory.LazyAttribute(
        lambda obj: DocumentFactory()
        if obj.is_document and fake.boolean(chance_of_getting_true=50)
        else None
    )
    blog_page = factory.LazyAttribute(
        lambda obj: None if obj.is_document else BlogPageFactory()
    )
