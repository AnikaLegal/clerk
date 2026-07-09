from django.urls import re_path

from . import views

urlpatterns = [
    # Catch-all: the intake form is a single page app whose client side router
    # owns all sub-paths (/intake/form/, /intake/resume/, exit pages etc).
    re_path(r".*", views.intake_view, name="intake-form"),
]
