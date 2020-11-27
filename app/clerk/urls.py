from django.conf.urls import include
from django.contrib import admin
from django.urls import path, re_path
from rest_framework import routers

from actionstep.views import start_oauth_view, end_oauth_view
from webhooks.views import webflow_form_view, jotform_form_view
from reports.views import reports_view, impact_view
from core import views as core_views

router = routers.SimpleRouter()
router.register("upload", core_views.UploadViewSet, basename="upload")
router.register("submission", core_views.SubmissionViewSet, basename="upload")

urlpatterns = [
    path("reports/impact.csv", impact_view, name="impact-csv"),
    re_path("^reports/(?P<path>.*)$", reports_view, name="reports"),
    path("admin/", admin.site.urls, name="admin"),
    path("actionstep/start/", start_oauth_view, name="actionstep-start"),
    path("actionstep/end/", end_oauth_view, name="actionstep-end"),
    path("api/webhooks/webflow-form/", webflow_form_view, name="webflow-form"),
    path("api/webhooks/jotform-form/", jotform_form_view, name="jotform-form"),
    path("api/", include(router.urls)),
]
