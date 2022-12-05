from django.db import models
from wagtail.core import blocks
from wagtail.core.models import Page
from wagtail.core.fields import StreamField
from wagtail.admin.edit_handlers import (
    FieldPanel,
    StreamFieldPanel,
    PrivacyModalPanel,
)
from wagtail.images.edit_handlers import ImageChooserPanel
from wagtail.images.blocks import ImageChooserBlock

from web.blocks import AttributedQuoteBlock
from .mixins import RICH_TEXT_FEATURES


class VolunteerListPage(Page):
    template = "web/volunteers/volunteer-list.html"
    subpage_types = ["web.VolunteerPage"]
    parent_page_types = ["web.RootPage"]

    def get_context(self, request):
        context = super().get_context(request)
        volunteer_pages = (
            self.get_children()
            .live()
            .specific()
            .public()
            .order_by("-first_published_at")
        )
        context["volunteer_pages"] = volunteer_pages
        return context


class VolunteerPage(Page):
    template = "web/volunteers/volunteer-details.html"
    parent_page_types = ["web.VolunteerListPage"]
    subpage_types = []

    body = StreamField(
        [
            ("heading", blocks.CharBlock(form_classname="full title")),
            ("paragraph", blocks.RichTextBlock(features=RICH_TEXT_FEATURES)),
            ("image", ImageChooserBlock()),
            ("quote", blocks.BlockQuoteBlock()),
            ("attributed_quote", AttributedQuoteBlock()),
        ]
    )
    position = models.CharField(max_length=255, help_text="The name of their role")
    main_image = models.ForeignKey(
        "wagtailimages.Image",
        related_name="+",
        on_delete=models.PROTECT,
        blank=True,
        null=True,
    )

    promote_panels = [FieldPanel("slug")]
    settings_panels = [PrivacyModalPanel()]
    content_panels = Page.content_panels + [
        FieldPanel("position"),
        ImageChooserPanel("main_image"),
        StreamFieldPanel("body"),
    ]

    def save(self, *args, **kwargs):
        self.search_description = f"{self.title}, {self.position} at Anika Legal"
        return super().save(*args, **kwargs)
