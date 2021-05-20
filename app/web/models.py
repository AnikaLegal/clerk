from django.db import models
from wagtail.core import blocks
from wagtail.core.models import Page
from wagtail.core.fields import StreamField
from wagtail.admin.edit_handlers import FieldPanel, StreamFieldPanel
from wagtail.images.edit_handlers import ImageChooserPanel
from wagtail.images.blocks import ImageChooserBlock

from accounts.models import User


class BlogListPage(Page):
    template = "web/blog/blog-list.html"
    subpage_types = ["web.BlogPage"]

    def get_context(self, request):
        context = super().get_context(request)
        blogs = self.get_children().live().order_by("-first_published_at")
        context["blogs"] = blogs
        return context


class BlogPage(Page):
    template = "web/blog/blog-details.html"
    parent_page_types = ["web.BlogListPage"]

    body = StreamField(
        [
            ("heading", blocks.CharBlock(form_classname="full title")),
            ("paragraph", blocks.RichTextBlock()),
            ("image", ImageChooserBlock()),
        ]
    )
    author = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    main_image = models.ForeignKey(
        "wagtailimages.Image",
        related_name="+",
        on_delete=models.PROTECT,
        blank=True,
        null=True,
    )
    content_panels = Page.content_panels + [
        FieldPanel("author"),
        ImageChooserPanel("main_image"),
        StreamFieldPanel("body"),
    ]
