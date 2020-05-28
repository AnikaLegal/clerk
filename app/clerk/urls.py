from django.conf.urls import include
from django.contrib import admin
from django.urls import path, re_path
from rest_framework import routers

from actionstep.views import start_oauth_view, end_oauth_view
from questions.views import apis
from webhooks.views import webflow_form_view
from .views import reports_view


router = routers.SimpleRouter()
router.register("submission", apis.SubmissionViewSet, basename="submission")
router.register("images", apis.ImageUploadViewSet, basename="images")
router.register("files", apis.FileUploadViewSet, basename="files")
urlpatterns = [
    re_path("^reports/(?P<path>.*)$", reports_view, name="reports"),
    path("admin/", admin.site.urls, name="admin"),
    path("actionstep/start/", start_oauth_view, name="actionstep-start"),
    path("actionstep/end/", end_oauth_view, name="actionstep-end"),
    path("api/webhooks/webflow-form/", webflow_form_view, name="webflow-form"),
    path("api/", include(router.urls)),
]
