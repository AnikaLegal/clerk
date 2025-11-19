import uuid

from django.contrib.contenttypes.fields import GenericRelation
from django.db import models
from wagtail.admin.panels import FieldPanel
from wagtail.models import DraftStateMixin, RevisionMixin


class Banner(DraftStateMixin, RevisionMixin, models.Model):  # pyright: ignore[reportIncompatibleVariableOverride]
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=128)
    subtitle = models.TextField(max_length=512, blank=True)
    image = models.ForeignKey(
        "wagtailimages.Image",
        related_name="+",
        on_delete=models.PROTECT,
        blank=True,
        null=True,
        help_text="""Minimum image width is 800px. Landscape images are
        preferable to portrait images. The ideal image ratio is 4:1, so the
        image should be sized 800x200px or any multiple thereof.""",
    )
    call_to_action_text = models.CharField(max_length=32)
    call_to_action_url = models.URLField()

    _revisions = GenericRelation("wagtailcore.Revision")

    panels = [
        FieldPanel("title"),
        FieldPanel("subtitle"),
        FieldPanel("image"),
        FieldPanel("call_to_action_text"),
        FieldPanel("call_to_action_url"),
    ]

    def save(self, *args, **kwargs):
        # Ensure only one live banner exists.
        if self.live:
            Banner.objects.filter(live=True).exclude(pk=self.pk).update(live=False)
        super().save(*args, **kwargs)
