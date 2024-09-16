from django.db import models
from wagtail import blocks
from wagtail.models import Page
from wagtail.fields import StreamField
from wagtail.admin.panels import FieldPanel
from wagtail.images.blocks import ImageChooserBlock

from web.blocks import AttributedQuoteBlock


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
            ("paragraph", blocks.RichTextBlock()),
            ("image", ImageChooserBlock()),
            ("quote", blocks.BlockQuoteBlock()),
            ("attributed_quote", AttributedQuoteBlock()),
        ],
        use_json_field=True
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
    content_panels = Page.content_panels + [
        FieldPanel("position"),
        FieldPanel("main_image"),
        FieldPanel("body"),
    ]

    def save(self, *args, **kwargs):
        self.search_description = f"{self.title}, {self.position} at Anika Legal"
        return super().save(*args, **kwargs)
