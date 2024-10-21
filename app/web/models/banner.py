from django.db import models
from wagtail.admin.panels import FieldPanel


class Banner(models.Model):
    title = models.CharField(max_length=128)
    subtitle = models.CharField(max_length=128, blank=True)
    image = models.ForeignKey(
        "wagtailimages.Image",
        related_name="+",
        on_delete=models.PROTECT,
        blank=True,
        null=True,
    )
    call_to_action_text = models.CharField(max_length=32)
    call_to_action_url = models.URLField()

    panels = [
        FieldPanel("title"),
        FieldPanel("subtitle"),
        FieldPanel("image"),
        FieldPanel("call_to_action_text"),
        FieldPanel("call_to_action_url"),
    ]