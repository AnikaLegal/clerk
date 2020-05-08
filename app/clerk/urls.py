from django.conf.urls import include
from django.contrib import admin
from django.urls import path
from rest_framework import routers

from questions.views import apis
from webhooks.views import webflow_form_view

router = routers.SimpleRouter()
router.register("submission", apis.SubmissionViewSet, basename="submission")
router.register("images", apis.ImageUploadViewSet, basename="images")
router.register("files", apis.FileUploadViewSet, basename="files")
urlpatterns = [
    path("admin/", admin.site.urls, name="admin"),
    path("api/webhooks/webflow-form/", webflow_form_view, name="webflow-form"),
    path("api/", include(router.urls)),
]
