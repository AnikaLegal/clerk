from django.contrib import admin
from django.urls import path
from rest_framework import routers

import questions.views as question_views
import questions.apis as question_apis


router = routers.DefaultRouter()
# router.register('questions/', question_apis.???, '?????')

urlpatterns = [
    path('api/', include(router.urls)),
    path('admin/', admin.site.urls),
    path('test/', question_views.IndexView.as_view(), name='index'),
    path('graph/', question_views.IndexView.as_view(), name='index'),
    path('', question_views.IndexView.as_view(), name='index'),
]
