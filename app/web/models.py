import os
from django.conf import settings

from django.db import models
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.http import Http404, HttpResponse
from wagtail.core import blocks, hooks
from wagtail.core.models import Page, Site
from wagtail.core.fields import StreamField
from wagtail.admin.edit_handlers import (
    FieldPanel,
    StreamFieldPanel,
    MultiFieldPanel,
    PrivacyModalPanel,
)
from wagtail.images.edit_handlers import ImageChooserPanel
from wagtail.images.blocks import ImageChooserBlock
from django.urls import re_path


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


# See here for details
# https://docs.wagtail.io/en/stable/advanced_topics/customisation/page_editing_interface.html#limiting-features-in-a-rich-text-field
RICH_TEXT_FEATURES = [
    "h2",
    "bold",
    "italic",  # bold / italic text
    "ol",
    "ul",  # ordered / unordered lists
    "link",  # page, external and email links
]


class WebRedirect(models.Model):
    class Meta:
        unique_together = ["source_path", "destination_path"]

    source_path = models.CharField(max_length=2048)
    destination_path = models.CharField(max_length=2048)
    is_permanent = models.BooleanField()

    def normalise_paths(self):
        self.source_path = self.source_path.strip("/")
        self.destination_path = "/" + self.destination_path.strip("/") + "/"
        if self.destination_path == "//":
            self.destination_path = "/"

    def save(self, *args, **kwargs):
        self.normalise_paths()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"from {self.source_path} to {self.destination_path}"


class NotFoundMixin:
    def serve(request, *args, **kwargs):
        raise Http404("Page does not exist.")


class MultiRootPageMixin:
    public_path = None
    wagtail_slug = None

    def get_private_path(self):
        return f"/cms/pages/{self.wagtail_slug}/"

    def get_url_parts(self, *args, **kwargs):
        site_id, root_url, page_path = super().get_url_parts(*args, **kwargs)
        new_path = None
        if page_path is not None:
            new_path = page_path.replace(self.get_private_path(), self.public_path)

        return site_id, root_url, new_path

    @classmethod
    def as_path(cls, name: str):
        def wagtail_serve_view(request, path):
            """
            Override default Wagtail 'serve' view.
            https://github.com/wagtail/wagtail/blob/main/wagtail/core/views.py#L12
            """
            site = Site.find_for_request(request)
            if not site:
                raise Http404

            path_components = [component for component in path.split("/") if component]

            # Begin hack: before this is Wagtail code.
            path_components = [cls.wagtail_slug] + path_components
            # End hack: after this is Wagtail code.

            page, args, kwargs = site.root_page.localized.specific.route(
                request, path_components
            )

            for fn in hooks.get_hooks("before_serve_page"):
                result = fn(page, request, args, kwargs)
                if isinstance(result, HttpResponse):
                    return result

            return page.serve(request, *args, **kwargs)

        url_prefix = cls.public_path.lstrip("/")
        url_re = f"^{url_prefix}((?:[\w\-]+/)*)$"
        return re_path(url_re, wagtail_serve_view, name=name)


class JobsRootMixin(MultiRootPageMixin):
    wagtail_slug = "jobs"
    public_path = "/about/jobs/"


class ResourceRootMixin(MultiRootPageMixin):
    wagtail_slug = "resources"
    public_path = "/resources/"


class BlogRootMixin(MultiRootPageMixin):
    wagtail_slug = "blog"
    public_path = "/blog/"


class RootPage(NotFoundMixin, Page):
    subpage_types = ["web.BlogListPage", "web.ResourceListPage", "web.JobListPage"]


class JobListPage(JobsRootMixin, Page):
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


class JobPage(JobsRootMixin, Page):
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


class ResourceListPage(NotFoundMixin, ResourceRootMixin, Page):
    subpage_types = ["web.ResourcePage"]
    parent_page_types = ["web.RootPage"]


class ResourcePage(ResourceRootMixin, Page):
    template = "web/resources/resource-page.html"
    parent_page_types = ["web.ResourceListPage"]
    subpage_types = []

    body = StreamField(
        [
            ("heading", blocks.CharBlock(form_classname="full title")),
            ("paragraph", blocks.RichTextBlock(features=RICH_TEXT_FEATURES)),
        ]
    )
    content_panels = Page.content_panels + [
        StreamFieldPanel("body"),
    ]


class BlogListPage(BlogRootMixin, Page):
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


class BlogPage(BlogRootMixin, Page):
    template = "web/blog/blog-details.html"
    parent_page_types = ["web.BlogListPage"]
    subpage_types = []

    body = StreamField(
        [
            ("heading", blocks.CharBlock(form_classname="full title")),
            ("paragraph", blocks.RichTextBlock(features=RICH_TEXT_FEATURES)),
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
