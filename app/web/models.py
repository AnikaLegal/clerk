from django.db import models
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.http import Http404
from wagtail.core import blocks
from wagtail.core.models import Page
from wagtail.core.fields import StreamField
from wagtail.admin.edit_handlers import (
    FieldPanel,
    StreamFieldPanel,
    MultiFieldPanel,
    PrivacyModalPanel,
)
from wagtail.images.edit_handlers import ImageChooserPanel
from wagtail.images.blocks import ImageChooserBlock


class NotFoundMixin:
    def serve(request, *args, **kwargs):
        raise Http404("Page does not exist.")


class RootPage(NotFoundMixin, Page):
    subpage_types = ["web.BlogListPage", "web.ResourceListPage"]


class ResourceListPage(NotFoundMixin, Page):
    public_path = "/resources/"
    private_path = "/cms/pages/resources/"

    subpage_types = ["web.ResourcePage"]
    parent_page_types = ["web.RootPage"]


class ResourcePage(Page):
    template = "web/resources/resource-page.html"
    parent_page_types = ["web.ResourceListPage"]
    subpage_types = []

    body = StreamField(
        [
            ("heading", blocks.CharBlock(form_classname="full title")),
            ("paragraph", blocks.RichTextBlock()),
        ]
    )
    content_panels = Page.content_panels + [
        StreamFieldPanel("body"),
    ]


class BlogListPage(Page):
    template = "web/blog/blog-list.html"
    subpage_types = ["web.BlogPage"]
    parent_page_types = ["web.RootPage"]
    blogs_per_page = 9

    def get_context(self, request):
        context = super().get_context(request)
        search = request.GET.get("search")
        blogs = self.get_children().live().public().order_by("-first_published_at")
        if search:
            blogs = blogs.search(search)

        page = request.GET.get("page")
        paginator = Paginator(blogs, self.blogs_per_page)
        try:
            blogs = paginator.page(page)
        except PageNotAnInteger:
            blogs = paginator.page(1)
        except EmptyPage:
            blogs = paginator.page(paginator.num_pages)

        context["blogs"] = blogs
        context["search"] = search or ""
        return context


class BlogPage(Page):

    template = "web/blog/blog-details.html"
    parent_page_types = ["web.BlogListPage"]
    subpage_types = []

    body = StreamField(
        [
            ("heading", blocks.CharBlock(form_classname="full title")),
            ("paragraph", blocks.RichTextBlock()),
            ("image", ImageChooserBlock()),
            ("quote", blocks.BlockQuoteBlock()),
        ]
    )
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
        FieldPanel("owner", heading="Author"),
        MultiFieldPanel(
            [
                ImageChooserPanel("main_image"),
                FieldPanel("search_description"),
            ],
            "Search and social media",
        ),
        StreamFieldPanel("body"),
    ]
