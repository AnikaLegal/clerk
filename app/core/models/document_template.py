import os
from urllib.parse import quote

from core.models.issue import CaseTopic
from core.models.timestamped import TimestampedModel
from django.db import models
from django.db.models import CharField, Value
from django.db.models.functions import Reverse, Right, StrIndex
from django.utils.text import slugify
from django_cleanup import cleanup
from microsoft.storage import MSGraphStorage

STORAGE_BASE_PATH = "templates"


class DocumentTemplateManager(models.Manager):
    def get_queryset(self):
        return (
            super()
            .get_queryset()
            .annotate(
                name=Right(
                    "file",
                    StrIndex(Reverse("file"), Value("/")) - 1,  # type: ignore
                    output_field=CharField(),
                ),
            )
        )


@cleanup.select
class DocumentTemplate(TimestampedModel):
    objects = DocumentTemplateManager()

    def _get_storage_class():
        return MSGraphStorage(enable_directory_caching=True)

    def _get_upload_to(self, filename):
        return os.path.join(slugify(STORAGE_BASE_PATH), slugify(self.topic), filename)

    topic = models.CharField(max_length=32, choices=CaseTopic.CHOICES)
    file = models.FileField(
        storage=_get_storage_class, upload_to=_get_upload_to, max_length=256
    )
