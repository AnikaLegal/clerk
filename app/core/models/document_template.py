import os
from core.models.issue import CaseSubtopic, CaseTopic
from core.models.timestamped import TimestampedModel
from django.db import models
from microsoft.storage import MSGraphStorage
from django.utils.text import slugify
from django_cleanup import cleanup


@cleanup.select
class DocumentTemplate(TimestampedModel):
    def _get_storage_class():
        return MSGraphStorage(base_path="templates")

    def _get_upload_to(instance, filename):
        topic = slugify(instance.topic)
        subtopic = slugify(instance.subtopic)
        path = os.path.join(topic, subtopic).rstrip("/")
        return os.path.join(path, filename)

    topic = models.CharField(max_length=32, choices=CaseTopic.CHOICES)
    subtopic = models.CharField(
        max_length=32, choices=CaseSubtopic.choices, default="", blank=True
    )
    file = models.FileField(
        storage=_get_storage_class, upload_to=_get_upload_to, max_length=256
    )
    name = models.CharField(max_length=256)

    def save(self, *args, **kwargs):
        self.name = os.path.basename(self.file.name)
        super().save(*args, **kwargs)
