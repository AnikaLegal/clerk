from wagtail.core.models import Page


from .mixins import NotFoundMixin


class RootPage(NotFoundMixin, Page):
    subpage_types = ["web.BlogListPage", "web.ResourceListPage", "web.JobListPage"]
