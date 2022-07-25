from django.urls import path
from . import views


urlpatterns = [
    path("receive/", views.receive_email_view),
    path("events/", views.events_email_view),
]
