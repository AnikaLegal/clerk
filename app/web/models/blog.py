from django.db import models
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from wagtail import blocks
from wagtail.models import Page
from wagtail.fields import StreamField
from wagtail.admin.panels import (
    FieldPanel,
    MultiFieldPanel,
)
from wagtail.images.blocks import ImageChooserBlock
from django.utils import translation
from django.template.response import TemplateResponse


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
        ],
        use_json_field=True,
    )
    main_image = models.ForeignKey(
        "wagtailimages.Image",
        related_name="+",
        on_delete=models.PROTECT,
        blank=True,
        null=True,
    )

    promote_panels = [FieldPanel("slug")]
    content_panels = Page.content_panels + [
        FieldPanel("owner", heading="Author"),
        MultiFieldPanel(
            [
                FieldPanel("main_image"),
                FieldPanel("search_description"),
            ],
            "Search and social media",
        ),
        FieldPanel("body"),
    ]

    def serve(self, request, *args, **kwargs):
        """Ensure links are translated as well."""
        resp = super().serve(request, *args, **kwargs)
        page = resp.context_data["page"]
        with translation.override(page.locale.language_code):
            resp.render()

        return resp
