from django.db import models
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from modelcluster.contrib.taggit import ClusterTaggableManager
from modelcluster.fields import ParentalKey
from taggit.models import TaggedItemBase
from wagtail import blocks
from wagtail.models import Page
from wagtail.fields import StreamField
from wagtail.admin.panels import (
    FieldPanel,
    MultiFieldPanel,
    ObjectList,
    TabbedInterface,
)
from wagtail.images.blocks import ImageChooserBlock
from django.utils import translation


class BlogListPage(Page):
    template = "web/blog/blog-list.html"
    subpage_types = ["web.BlogPage"]
    parent_page_types = ["web.RootPage"]
    blogs_per_page = 9

    def get_context(self, request):
        context = super().get_context(request)
        blogs = self.get_children().live().public().order_by("-first_published_at")

        search = request.GET.get("search")
        if search:
            blogs = blogs.autocomplete(search)

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


class BlogPageTag(TaggedItemBase):
    content_object = ParentalKey(
        "BlogPage",
        related_name="tagged_items",
        on_delete=models.CASCADE,
    )


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
    tags = ClusterTaggableManager(through="web.BlogPageTag", blank=True)
    main_image = models.ForeignKey(
        "wagtailimages.Image",
        related_name="+",
        on_delete=models.PROTECT,
        blank=True,
        null=True,
    )

    promote_panels = Page.promote_panels + [
        MultiFieldPanel(
            [
                FieldPanel("main_image"),
            ],
            "For social media",
        ),
    ]
    content_panels = Page.content_panels + [
        FieldPanel("owner", heading="Author"),
        FieldPanel("body"),
    ]
    tag_panels = [
        FieldPanel("tags"),
    ]

    edit_handler = TabbedInterface(
        [
            ObjectList(content_panels, heading="Content"),
            ObjectList(tag_panels, heading="Tags"),
            ObjectList(promote_panels, heading="Promote"),
        ]
    )

    def serve(self, request, *args, **kwargs):
        """Ensure links are translated as well."""
        resp = super().serve(request, *args, **kwargs)
        page = resp.context_data["page"]
        with translation.override(page.locale.language_code):
            resp.render()

        return resp

    def get_context(self, request, *args, **kwargs):
        from web.forms import ContentFeedbackForm

        context = super().get_context(request, *args, **kwargs)
        context["feedback_form"] = ContentFeedbackForm()
        return context
