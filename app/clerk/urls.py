from django.conf import settings
from django.conf.urls import include, re_path
from django.contrib import admin
from django.urls import path
from django.views.generic.base import RedirectView
from rest_framework import routers

import questions.apis as question_apis
import questions.views as question_views

# TODO - get this into a context processort so we don't hardcode URLs in the frontend.
router = routers.DefaultRouter()
router.register('questions/script', question_apis.ScriptViewSet, 'questions-script')
router.register('questions/question', question_apis.QuestionViewSet, 'questions-question')
router.register('questions/submission', question_apis.SubmissionViewSet, 'questions-submission')
urlpatterns = [
    path('api/', include(router.urls)),
    path('admin/', admin.site.urls),
    # React single page app URLs
    re_path('^questionnaire/', question_views.IndexView.as_view(), name='index'),
    path('', RedirectView.as_view(url='/questionnaire/')),
]

if settings.DEBUG:
    import debug_toolbar
    urlpatterns = [
        path('__debug__/', include(debug_toolbar.urls)),
    ] + urlpatterns
