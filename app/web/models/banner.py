import uuid

from django.db import models
from wagtail.admin.panels import FieldPanel


class Banner(models.Model):
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
    is_active = models.BooleanField(default=False)

    panels = [
        FieldPanel("is_active"),
        FieldPanel("title"),
        FieldPanel("subtitle"),
        FieldPanel("image"),
        FieldPanel("call_to_action_text"),
        FieldPanel("call_to_action_url"),
    ]

    def save(self, *args, **kwargs):
        # Ensure only one active record exists
        if self.is_active:
            Banner.objects.filter(is_active=True).exclude(pk=self.pk).update(
                is_active=False
            )
        super().save(*args, **kwargs)

    @classmethod
    def get_active(cls):
        return cls.objects.filter(is_active=True).last()
