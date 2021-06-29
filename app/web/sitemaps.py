from django.contrib import sitemaps
from django.urls import reverse

from .models import ResourcePage, BlogListPage, BlogPage, JobListPage, JobPage


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
        ]

    def location(self, item):
        return reverse(item)


class JobSitemap(sitemaps.Sitemap):
    priority = 0.5
    changefreq = "daily"

    def items(self):
        return [*JobListPage.objects.all(), *JobPage.objects.all()]

    def location(self, item):
        return item.url


class BlogSitemap(sitemaps.Sitemap):
    priority = 0.5
    changefreq = "daily"

    def items(self):
        return [*BlogListPage.objects.all(), *BlogPage.objects.all()]

    def location(self, item):
        return item.url


class ResourceSitemap(sitemaps.Sitemap):
    priority = 0.5
    changefreq = "daily"

    def items(self):
        return ResourcePage.objects.all()

    def location(self, item):
        return item.url


SITEMAPS = {
    "static": StaticSitemap,
    "blog": BlogSitemap,
    "resources": ResourceSitemap,
    "jobs": JobSitemap,
}
