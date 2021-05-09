from django.urls import path
from django.views.generic import TemplateView

from . import views


def template(name):
    return TemplateView.as_view(template_name=name)


# Views where the path, name and template name are the same.
repeated_names = [
    "rental-help",
    "about",
    "team",
    "partners",
    "impact",
    "resources",
    "terms-of-use",
    "eligibility-criteria",
    "privacy-policy",
    "collections-statement",
]

repeated_paths = [
    path(f"{n}/", template(f"web/{n}.html"), name=n) for n in repeated_names
]


urlpatterns = repeated_paths + [
    path("services/rental-repairs/", template("web/repairs.html"), name="repairs"),
    path(
        "services/eviction-support/", template("web/evictions.html"), name="evictions"
    ),
    # TODO: Blog and blog articles (by slug)
    # path("/blog/", ???, name="blog"),
    path("robots.txt", views.robots_view),
    path("landing/contact/", views.landing_contact_form_view, name="landing-contact"),
    path("", views.landing_view, name="landing"),
]
