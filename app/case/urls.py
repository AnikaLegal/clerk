from django.urls import include, path

from . import views

urlpatterns = [
    path("robots.txt", views.robots_view),
    # Auth
    path("oauth/", include("social_django.urls", namespace="social")),
    path("login/", views.login_view, name="login"),
    path("logout/", views.logout_view, name="logout"),
    # Cases
    path("cases/", views.case_list_view, name="case-list"),
    path("cases/<uuid:pk>/", views.case_detail_view, name="case-detail"),
    path(
        "cases/<uuid:pk>/progress/",
        views.case_detail_progress_view,
        name="case-detail-progress",
    ),
    path("", views.root_view, name="root"),
]
