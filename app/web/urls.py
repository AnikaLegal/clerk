from django.urls import path, re_path
from django.conf.urls import include
from django.views.generic import TemplateView
from wagtail.admin import urls as wagtailadmin_urls
from wagtail.core import urls as wagtail_urls
from wagtail.documents import urls as wagtaildocs_urls
from .models import ResourceListPage, BlogListPage

from . import views


def template(name):
    return TemplateView.as_view(template_name=name)


urlpatterns = [
    # Jobs
    path("openings/", template("web/openings.html"), name="openings"),
    # About
    path("about/", template("web/about/about.html"), name="about"),
    path("about/annual-reports/", template("web/about/reports.html"), name="reports"),
    path("about/team/", views.team_view, name="team"),
    path("about/impact/", template("web/about/impact.html"), name="impact"),
    path("about/join-our-team/", template("web/jobs/job-list.html"), name="jobs"),
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
    # Robots.txt
    path("robots.txt", views.robots_view),
    # Landing page
    path("landing/contact/", views.landing_contact_form_view, name="landing-contact"),
    re_path(r"^$", views.landing_view, name="landing"),
    re_path(r"^(?P<path>.*)$", views.not_found_view, name="not-found"),
]
