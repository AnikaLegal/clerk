import os
from django.conf import settings

from django.db import models
from wagtail.core import blocks
from wagtail.core.models import Page
from wagtail.core.fields import StreamField
from wagtail.admin.edit_handlers import (
    FieldPanel,
    StreamFieldPanel,
    PrivacyModalPanel,
)
from wagtail.images.blocks import ImageChooserBlock

from .mixins import RICH_TEXT_FEATURES


ICONS_DIR = os.path.join(
    settings.BASE_DIR, "..", "web", "static", "web", "img", "icons"
)
ICONS = [os.path.join("web", "img", "icons", i) for i in os.listdir(ICONS_DIR)]
ICON_CHOICES = (
    (
        i,
        i.split("/")[-1].split(".")[0],
    )
    for i in ICONS
)


class JobListPage(Page):
    template = "web/jobs/job-list.html"
    subpage_types = ["web.JobPage"]
    parent_page_types = ["web.RootPage"]

    def get_context(self, request):
        context = super().get_context(request)
        jobs = (
            self.get_children()
            .live()
            .specific()
            .public()
            .order_by("-first_published_at")
        )
        context["jobs"] = jobs
        return context


class JobPage(Page):
    template = "web/jobs/job-details.html"
    parent_page_types = ["web.JobListPage"]
    subpage_types = []
    icon = models.CharField(max_length=64, choices=ICON_CHOICES)
    closing_date = models.DateField()
    body = StreamField(
        [
            ("heading", blocks.CharBlock(form_classname="full title")),
            ("paragraph", blocks.RichTextBlock(features=RICH_TEXT_FEATURES)),
            ("image", ImageChooserBlock()),
        ]
    )
    promote_panels = [FieldPanel("slug")]
    settings_panels = [PrivacyModalPanel()]
    content_panels = Page.content_panels + [
        FieldPanel("icon", heading="Icon"),
        FieldPanel("closing_date", heading="Application closing date"),
        FieldPanel("search_description", heading="Short description"),
        StreamFieldPanel("body", heading="Long description"),
    ]
