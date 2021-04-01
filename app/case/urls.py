from django.urls import include, path

from . import views

urlpatterns = [
    path("robots.txt", views.RobotsView.as_view()),
    # Auth
    path("oauth/", include("social_django.urls", namespace="social")),
    path("login/", views.LoginView.as_view(), name="login"),
    # Example
    path("", views.ExampleView.as_view(), name="example"),
]
