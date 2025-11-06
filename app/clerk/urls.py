from caller.views import answer_view, collect_view, message_view
from core import views as core_views
from debug_toolbar.toolbar import debug_toolbar_urls
from django.conf import settings
from django.conf.urls import include
from django.conf.urls.i18n import i18n_patterns
from django.contrib import admin
from django.contrib.sitemaps.views import sitemap
from django.urls import path, re_path
from django.views.generic import TemplateView
from django.views.generic.base import RedirectView
from emails import urls as email_urls
from rest_framework import routers
from wagtail import urls as wagtail_urls
from wagtail.admin import urls as wagtailadmin_urls
from wagtail.documents import urls as wagtaildocs_urls
from web import views
from web.sitemaps import SITEMAPS
from webhooks.views import intake_no_email_view, jotform_form_view, webflow_form_view


def template(name):
    return TemplateView.as_view(template_name=name)


router = routers.SimpleRouter()
router.register("upload", core_views.UploadViewSet, basename="upload")
router.register("submission", core_views.SubmissionViewSet, basename="submission")

urlpatterns = [
    path("oauth/", include("social_django.urls", namespace="social")),
    path("admin/", admin.site.urls, name="admin"),
    # TODO: Move to caller
    path("caller/answer/", answer_view, name="caller-answer"),
    path("caller/collect/", collect_view, name="caller-collect"),
    path("caller/message/", message_view, name="caller-message"),
    # TODO: Move to webhooks
    path("api/webhooks/webflow-form/", webflow_form_view, name="webflow-form"),
    path("api/webhooks/jotform-form/", jotform_form_view, name="jotform-form"),
    path("api/webhooks/intake-noemail/", intake_no_email_view, name="intake-noemail"),
    # TODO: Move router to core
    path("api/", include(router.urls)),
    path("clerk/", include("case.urls")),
    path("launch/", include("intake.urls")),
    re_path(r"^case/(?P<path>.*)", RedirectView.as_view(url="/clerk/%(path)s")),
    path("accounts/", include("accounts.urls")),
    path("email/", include(email_urls)),
    # About
    path("about/", template("web/about/about.html"), name="about"),
    path("about/annual-reports/", template("web/about/reports.html"), name="reports"),
    path("about/team/", views.team_view, name="team"),
    path("about/impact/", views.impact_view, name="impact"),
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
        "services/bond-recovery/",
        template("web/services/bonds.html"),
        name="bonds",
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
    # Partners
    path(
        "partners/philanthropy/",
        template("web/partners/philanthropy.html"),
        name="philanthropy-partners",
    ),
    path(
        "partners/corporates/",
        template("web/partners/corporates.html"),
        name="corporate-partners",
    ),
    path(
        "partners/universities/",
        template("web/partners/universities.html"),
        name="university-partners",
    ),
    path(
        "partners/community-organisations/",
        template("web/partners/community-organisations.html"),
        name="community-partners",
    ),
    path(
        "partners/law-students/",
        template("web/partners/law-students.html"),
        name="law-student-partners",
    ),
    path(
        "subscribe/",
        template("web/subscribe.html"),
        name="subscribe",
    ),
    # Wagtail admin - excluded by robots.txt
    path("cms/admin/", include(wagtailadmin_urls)),
    path("cms/documents/", include(wagtaildocs_urls)),
    path("blog/search/", views.blog_search_view, name="blog-search"),
    # Dashboard.
    path("dash/", views.dashboard_view, name="dashboard"),
    # Robots.txt
    path("robots.txt", views.robots_view),
    # Sitemap
    path(
        "sitemap.xml",
        sitemap,
        {"sitemaps": SITEMAPS},
        name="django.contrib.sitemaps.views.sitemap",
    ),
    # Landing page
    path("landing/contact/", views.landing_contact_form_view, name="landing-contact"),
    path("feedback/", views.content_feedback_form_view, name="content-feedback"),
    re_path(r"^$", views.landing_view, name="landing"),
]
if settings.DEBUG:
    urlpatterns += [
        path("__reload__/", include("django_browser_reload.urls")),
    ]
    urlpatterns += debug_toolbar_urls()


# Wagtail pages + internationalized urls
urlpatterns += i18n_patterns(
    path("", include(wagtail_urls)),
    prefix_default_language=False,
)
