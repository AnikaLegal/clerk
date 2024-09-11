from django.db import models
from wagtail.admin.panels import FieldPanel


class DashboardItem(models.Model):
    title = models.CharField(max_length=128)
    link = models.URLField()
    description = models.TextField(blank=True, default="")
    icon = models.ForeignKey(
        "wagtailimages.Image",
        related_name="+",
        on_delete=models.PROTECT,
        blank=True,
        null=True,
    )
    panels = [
        FieldPanel("title"),
        FieldPanel("link"),
        FieldPanel("icon"),
        FieldPanel("description"),
    ]
