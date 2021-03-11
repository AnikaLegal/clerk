from django.urls import path

from . import views

urlpatterns = [
    path("robots.txt", views.RobotsView.as_view()),
    path("", views.ExampleView.as_view()),
]
