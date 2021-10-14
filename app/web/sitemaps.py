from django.contrib import sitemaps
from django.urls import reverse

from .models import (
    ResourcePage,
    BlogListPage,
    BlogPage,
    JobListPage,
    JobPage,
    NewsListPage,
    NewsPage,
    VolunteerListPage,
    VolunteerPage,
)


class StaticSitemap(sitemaps.Sitemap):
    priority = 0.5
    changefreq = "daily"

    def items(self):
        return [
            "about",
            "reports",
            "team",
            "impact",
            "services",
            "repairs",
            "evictions",
            "refer",
            "philanthropy-partners",
            "corporate-partners",
            "university-partners",
            "community-partners",
            "law-student-partners",
        ]

    def location(self, item):
        return reverse(item)


class WagtailSitemap(sitemaps.Sitemap):
    priority = 0.5
    changefreq = "daily"
    list_page = None
    details_page = None

    def items(self):
        items = []
        if self.list_page:
            items += list(self.list_page.objects.all())
        if self.details_page:
            items += list(self.details_page.objects.all())

        return items

    def location(self, item):
        return item.url


class JobSitemap(WagtailSitemap):
    list_page = JobListPage
    details_page = JobPage


class BlogSitemap(WagtailSitemap):
    list_page = BlogListPage
    details_page = BlogPage


class ResourceSitemap(WagtailSitemap):
    details_page = ResourcePage


class NewsSitemap(WagtailSitemap):
    list_page = NewsListPage
    details_page = NewsPage


class VolunteerSitemap(WagtailSitemap):
    list_page = VolunteerListPage
    details_page = VolunteerPage


SITEMAPS = {
    "static": StaticSitemap,
    "blog": BlogSitemap,
    "resources": ResourceSitemap,
    "jobs": JobSitemap,
    "news": NewsSitemap,
    "volunteers": VolunteerSitemap,
}
