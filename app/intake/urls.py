from django.urls import path, re_path

from . import views

urlpatterns = [
    re_path(".*", views.intake_view, name="intake-form"),
]
