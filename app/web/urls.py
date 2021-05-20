from django.urls import path
from django.views.generic import TemplateView

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
    path("openings/", template("web/openings.html"), name="openings"),
    path("about/", template("web/about/about.html"), name="about"),
    path("about/annual-reports/", template("web/about/reports.html"), name="reports"),
    path("about/team/", views.team_view, name="team"),
    path("about/impact/", template("web/about/impact.html"), name="impact"),
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
    path("blog/", views.BlogListView.as_view(), name="blog"),
    path("blog/<int:pk>/", views.BlogDetailView.as_view(), name="blog-detail"),
    path("robots.txt", views.robots_view),
    path("landing/contact/", views.landing_contact_form_view, name="landing-contact"),
    path("", views.landing_view, name="landing"),
]
