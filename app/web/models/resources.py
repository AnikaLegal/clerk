from wagtail import blocks
from wagtail.models import Page
from wagtail.fields import StreamField
from wagtail.admin.panels import FieldPanel
from .mixins import NotFoundMixin


class ResourceListPage(NotFoundMixin, Page):
    subpage_types = ["web.ResourcePage"]
    parent_page_types = ["web.RootPage"]


class ResourcePage(Page):
    template = "web/resources/resource-page.html"
    parent_page_types = ["web.ResourceListPage"]
    subpage_types = []

    def get_template(self, request, *args, **kwargs):
        from django.template.loader import get_template
        from django.template.exceptions import TemplateDoesNotExist

        slug_template = f"web/resources/{self.slug}.html"
        try:
            get_template(slug_template)
            return slug_template
        except TemplateDoesNotExist:
            return self.template

    body = StreamField(
        [
            ("heading", blocks.CharBlock(form_classname="full title")),
            ("paragraph", blocks.RichTextBlock()),
        ],
        use_json_field=True
    )
    content_panels = Page.content_panels + [
        FieldPanel("body"),
    ]
