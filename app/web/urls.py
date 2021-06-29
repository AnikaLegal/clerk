from django.urls import path, re_path
from django.conf.urls import include
from django.views.generic import TemplateView
from django.contrib.sitemaps.views import sitemap
from wagtail.admin import urls as wagtailadmin_urls
from wagtail.core import urls as wagtail_urls
from wagtail.documents import urls as wagtaildocs_urls
from .models import ResourceListPage, BlogListPage, JobListPage
from .sitemaps import SITEMAPS

from . import views


def template(name):
    return TemplateView.as_view(template_name=name)


urlpatterns = [
    # About
    path("about/", template("web/about/about.html"), name="about"),
    path("about/annual-reports/", template("web/about/reports.html"), name="reports"),
    path("about/team/", views.team_view, name="team"),
    path("about/impact/", template("web/about/impact.html"), name="impact"),
    # Services
    path(
        "services/",
        template("web/services/services.html"),
        name="services",
    ),
    path(
        "services/rental-repairs/",
        template("web/services/repairs.html"),
        name="repairs",
    ),
    path(
        "services/eviction-support/",
        template("web/services/evictions.html"),
        name="evictions",
    ),
    path(
        "services/refer-someone/",
        template("web/services/refer-someone.html"),
        name="refer",
    ),
    # Wagtail
    path("cms/admin/", include(wagtailadmin_urls)),
    path("cms/documents/", include(wagtaildocs_urls)),
    path("cms/pages/", include(wagtail_urls)),
    path("blog/search/", views.blog_search_view, name="blog-search"),
    ResourceListPage.as_path("resources"),
    BlogListPage.as_path("blog"),
    JobListPage.as_path("jobs"),
    # Robots.txt
    path("robots.txt", views.robots_view),
    path(
        "sitemap.xml",
        sitemap,
        {"sitemaps": SITEMAPS},
        name="django.contrib.sitemaps.views.sitemap",
    ),
    # Landing page
    path("landing/contact/", views.landing_contact_form_view, name="landing-contact"),
    re_path(r"^$", views.landing_view, name="landing"),
]
