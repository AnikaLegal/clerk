from django.urls import path

from . import views

urlpatterns = [
    path("", views.intake_view, name="intake-landing"),
]
