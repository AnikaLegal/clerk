from django.urls import path
from django.conf.urls import include
from django.views.generic import TemplateView
from wagtail.admin import urls as wagtailadmin_urls
from wagtail.core import urls as wagtail_urls
from wagtail.documents import urls as wagtaildocs_urls

from . import views


def template(name):
    return TemplateView.as_view(template_name=name)


urlpatterns = [
    path(
        "terms-of-use/", template("web/legalese/terms-of-use.html"), name="terms-of-use"
    ),
    path(
        "eligibility-criteria/",
        template("web/legalese/eligibility-criteria.html"),
        name="eligibility-criteria",
    ),
    path(
        "privacy-policy/",
        template("web/legalese/privacy-policy.html"),
        name="privacy-policy",
    ),
    path(
        "collections-statement/",
        template("web/legalese/collections-statement.html"),
        name="collections-statement",
    ),
    # path(
    #     "partnerships/philanthropy",
    #     template("web/philanthropy.html"),
    #     name="philanthropy",
    # ),
    # path("partnerships/corporates", template("web/corporates.html"), name="corporates"),
    # path(
    #     "partnerships/universities",
    #     template("web/universities.html"),
    #     name="universities",
    # ),
    # path(
    #     "partnerships/community",
    #     template("web/partnerships/community.html"),
    #     name="community",
    # ),
    path(
        "resources/community",
        template("web/resources/community.html"),
        name="refer",
    ),
    # Jobs
    path("openings/", template("web/openings.html"), name="openings"),
    # About
    path("about/", template("web/about/about.html"), name="about"),
    path("about/annual-reports/", template("web/about/reports.html"), name="reports"),
    path("about/team/", views.team_view, name="team"),
    path("about/impact/", template("web/about/impact.html"), name="impact"),
    # Services
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
    # Wagtail
    path("cms/admin/", include(wagtailadmin_urls)),
    path("cms/documents/", include(wagtaildocs_urls)),
    path("blog/", include(wagtail_urls), name="blog"),
    # Robots.txt
    path("robots.txt", views.robots_view),
    # Landing page
    path("landing/contact/", views.landing_contact_form_view, name="landing-contact"),
    path("", views.landing_view, name="landing"),
]
