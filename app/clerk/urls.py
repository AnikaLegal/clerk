from django.conf.urls import include
from django.contrib import admin
from django.urls import path, re_path
from django.conf import settings
from rest_framework import routers
from django.views.generic.base import RedirectView

from web import urls as web_urls
from emails import urls as email_urls
from actionstep.views import end_oauth_view, start_oauth_view
from caller.views import answer_view, collect_view, message_view
from core import views as core_views
from webhooks.views import jotform_form_view, webflow_form_view


router = routers.SimpleRouter()
router.register("upload", core_views.UploadViewSet, basename="upload")
router.register("submission", core_views.SubmissionViewSet, basename="submission")
router.register("noemail", core_views.NoEmailViewSet, basename="noemail")

urlpatterns = [
    path("oauth/", include("social_django.urls", namespace="social")),
    path("admin/", admin.site.urls, name="admin"),
    # TODO: Move to Actionstep
    path("actionstep/start/", start_oauth_view, name="actionstep-start"),
    path("actionstep/end/", end_oauth_view, name="actionstep-end"),
    # TODO: Move to caller
    path("caller/answer/", answer_view, name="caller-answer"),
    path("caller/collect/", collect_view, name="caller-collect"),
    path("caller/message/", message_view, name="caller-message"),
    # TODO: Move to webhooks
    path("api/webhooks/webflow-form/", webflow_form_view, name="webflow-form"),
    path("api/webhooks/jotform-form/", jotform_form_view, name="jotform-form"),
    # TODO: Move router to core
    path("api/", include(router.urls)),
    path("clerk/", include("case.urls")),
    re_path(r"^case/(?P<path>.*)", RedirectView.as_view(url="/clerk/%(path)s")),
    path("accounts/", include("accounts.urls")),
    path("email/", include(email_urls)),
    path("", include(web_urls)),
]

if settings.DEBUG:
    urlpatterns += [
        path("__reload__/", include("django_browser_reload.urls")),
        path("__debug__/", include("debug_toolbar.urls")),
    ]
