from django.contrib import sitemaps
from django.urls import reverse

from .models import ResourcePage, BlogListPage, BlogPage


class StaticSitemap(sitemaps.Sitemap):
    priority = 0.5
    changefreq = "daily"

    def items(self):
        return [
            "about",
            "reports",
            "team",
            "impact",
            "jobs",
            "services",
            "repairs",
            "evictions",
            "refer",
        ]

    def location(self, item):
        return reverse(item)


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
}
