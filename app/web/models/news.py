from django.db import models
from wagtail import blocks
from wagtail.models import Page
from wagtail.fields import StreamField
from wagtail.admin.panels import FieldPanel

from wagtail.images.blocks import ImageChooserBlock


class NewsListPage(Page):
    template = "web/news/news-list.html"
    subpage_types = ["web.NewsPage"]
    parent_page_types = ["web.RootPage"]

    def get_context(self, request):
        context = super().get_context(request)
        external_articles = ExternalNews.objects.order_by("-published_date").all()
        articles = (
            self.get_children()
            .live()
            .specific()
            .public()
            .order_by("-first_published_at")
        )
        context["articles"] = articles
        context["external_articles"] = external_articles
        return context


class NewsPage(Page):
    template = "web/news/news-details.html"
    parent_page_types = ["web.NewsListPage"]
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
    promote_panels = [FieldPanel("slug")]
    content_panels = Page.content_panels + [
        FieldPanel("owner", heading="Author"),
        FieldPanel("search_description", heading="Social description"),
        FieldPanel("body"),
    ]


class ExternalNews(models.Model):
    title = models.CharField(max_length=128)
    published_date = models.DateField()
    url = models.URLField()
    brand_image = models.ForeignKey(
        "wagtailimages.Image",
        related_name="+",
        on_delete=models.PROTECT,
        blank=True,
        null=True,
    )
    panels = [
        FieldPanel("title"),
        FieldPanel("published_date"),
        FieldPanel("url"),
        FieldPanel("brand_image"),
    ]

    class Meta:
        verbose_name_plural = "external news"
