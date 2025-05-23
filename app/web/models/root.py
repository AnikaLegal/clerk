from wagtail.models import Page


from .mixins import NotFoundMixin


class RootPage(NotFoundMixin, Page):
    subpage_types = [
        "web.BlogListPage",
        "web.ResourceListPage",
        "web.JobListPage",
        "web.NewsListPage",
        "web.VolunteerListPage",
    ]
