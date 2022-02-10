from django.urls import path

from .views.client import router as client_router
from .views.paralegal import router as paralegal_router
from .views.person import router as person_router
from .views.tenancy import router as tenancy_router
from .views.accounts import router as accounts_router
from .views.templates import router as templates_router
from .views.case import router as case_router

from .views import root

urlpatterns = [
    path("paralegals/", paralegal_router.include()),
    path("parties/", person_router.include()),
    path("tenancy/", tenancy_router.include()),
    path("client/", client_router.include()),
    path("accounts/", accounts_router.include()),
    path("templates/", templates_router.include()),
    path("cases/", case_router.include()),
    path("not-allowed/", root.not_allowed_view, name="case-not-allowed"),
    path("", root.root_view, name="case-root"),
]
