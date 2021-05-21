from django.db import models
from wagtail.core import blocks
from wagtail.core.models import Page
from wagtail.core.fields import StreamField
from wagtail.admin.edit_handlers import FieldPanel, StreamFieldPanel
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from wagtail.images.edit_handlers import ImageChooserPanel
from wagtail.images.blocks import ImageChooserBlock


BLOGS_PER_PAGE = 9


class BlogListPage(Page):
    template = "web/blog/blog-list.html"
    subpage_types = ["web.BlogPage"]

    def get_context(self, request):
        context = super().get_context(request)
        search = request.GET.get("search")
        blogs = self.get_children().live().public().order_by("-first_published_at")
        if search:
            blogs = blogs.search(search)

        page = request.GET.get("page")
        paginator = Paginator(blogs, BLOGS_PER_PAGE)
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
    content_panels = Page.content_panels + [
        FieldPanel("owner"),
        ImageChooserPanel("main_image"),
        FieldPanel("search_description"),
        StreamFieldPanel("body"),
    ]
