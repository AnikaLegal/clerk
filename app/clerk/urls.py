from django.conf.urls import include
from django.contrib import admin
from django.urls import path
from rest_framework import routers

from questions.views import apis

router = routers.DefaultRouter()
urlpatterns = [
    path('admin/', admin.site.urls, name='admin'),
    path('api/', include(router.urls)),
]
