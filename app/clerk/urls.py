from django.conf.urls import include
from django.contrib import admin
from django.urls import path
from rest_framework import routers

from actionstep.views import start_oauth_view, end_oauth_view
from webhooks.views import webflow_form_view, jotform_form_view
<<<<<<< HEAD
from caller.views import answer_view, collect_view
=======
from reports.views import reports_view
from caller.views import answer_view, collect_view, message_view
>>>>>>> Create Call model and migration
from core import views as core_views

router = routers.SimpleRouter()
router.register("upload", core_views.UploadViewSet, basename="upload")
router.register("submission", core_views.SubmissionViewSet, basename="submission")

urlpatterns = [
    path("admin/", admin.site.urls, name="admin"),
    path("actionstep/start/", start_oauth_view, name="actionstep-start"),
    path("actionstep/end/", end_oauth_view, name="actionstep-end"),
    path("api/webhooks/webflow-form/", webflow_form_view, name="webflow-form"),
    path("api/webhooks/jotform-form/", jotform_form_view, name="jotform-form"),
    path("caller/answer/", answer_view, name="caller-answer"),
    path("caller/collect/", collect_view, name="caller-collect"),
    path("caller/message/", message_view, name="caller-message"),
    path("api/", include(router.urls)),
]
