from django.urls import include, path, re_path
from rest_framework.routers import DefaultRouter

from .views.client import router as client_router
from .views.paralegal import router as paralegal_router
from .views import person, tenancy
from .views.accounts import router as accounts_router
from .views.templates import router as templates_router
from .views.case import router as case_router

from .views import root

INT_PK = "(?P<pk>[0-9]+)"

router = DefaultRouter()
router.register("person", person.PersonApiViewset, basename="person-api")
router.register("tenancy", tenancy.TenancyApiViewset, basename="tenancy-api")

urlpatterns = [
    # API routes
    path("api/", include(router.urls)),
    # Parties
    path("parties/", person.person_list_page_view, name="person-list"),
    path("parties/create/", person.person_create_page_view, name="person-create"),
    re_path(
        f"^parties/{INT_PK}/$", person.person_detail_page_view, name="person-detail"
    ),
    # Tenancies
    re_path(
        f"^tenancy/{INT_PK}/$", tenancy.tenancy_detail_page_view, name="tenancy-detail"
    ),
    # Custom router urls: we are removing these one-by-one.
    path("paralegals/", paralegal_router.include()),
    path("client/", client_router.include()),
    path("accounts/", accounts_router.include()),
    path("templates/", templates_router.include()),
    path("cases/", case_router.include()),
    path("", root.root_view, name="case-root"),
]
