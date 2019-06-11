from django.conf.urls import include
from django.contrib import admin
from django.urls import path
from rest_framework import routers

from questions.views import apis

router = routers.SimpleRouter()
router.register("submission", apis.SubmissionViewSet, basename="submission")
router.register("images", apis.ImageUploadViewSet, basename="images")
urlpatterns = [path("admin/", admin.site.urls, name="admin"), path("api/", include(router.urls))]
