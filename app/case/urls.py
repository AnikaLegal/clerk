from django.urls import include, path, re_path
from rest_framework.routers import DefaultRouter

from .views import person, tenancy, client, accounts, paralegal
from .views.templates import router as templates_router
from .views.case import router as case_router

from .views import root

INT_PK = "(?P<pk>[0-9]+)"
UUID_PK = "(?P<pk>[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-4[0-9a-fA-F]{3}-[89abAB][0-9a-fA-F]{3}-[0-9a-fA-F]{12})"

router = DefaultRouter()
router.register("person", person.PersonApiViewset, basename="person-api")
router.register("tenancy", tenancy.TenancyApiViewset, basename="tenancy-api")
router.register("client", client.ClientApiViewset, basename="client-api")
router.register("account", accounts.AccountApiViewset, basename="account-api")


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
    # Client
    re_path(
        f"^client/{UUID_PK}/$", client.client_detail_page_view, name="client-detail"
    ),
    # Accounts
    path("account/", accounts.account_list_page_view, name="account-list"),
    path("account/create/", accounts.account_create_page_view, name="account-create"),
    re_path(
        f"^account/{INT_PK}/$", accounts.account_detail_page_view, name="account-detail"
    ),
    # Paralegals
    path("paralegals/", paralegal.paralegal_list_page_view, name="paralegal-list"),
    # Custom router urls: we are removing these one-by-one.
    path("templates/", templates_router.include()),
    path("cases/", case_router.include()),
    path("", root.root_view, name="case-root"),
]
