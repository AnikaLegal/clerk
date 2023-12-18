from django.urls import include, path, re_path
from rest_framework.routers import DefaultRouter

from .views import person, tenancy, client, accounts, paralegal
from .views.templates import (
    templates_list,
    email_templates,
    notification_templates,
    document_templates,
)
from .views.case import router as case_router

from .views import root

INT_PK = "(?P<pk>[0-9]+)"
UUID_PK = "(?P<pk>[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-4[0-9a-fA-F]{3}-[89abAB][0-9a-fA-F]{3}-[0-9a-fA-F]{12})"

router = DefaultRouter()
router.register("person", person.PersonApiViewset, basename="person-api")
router.register("tenancy", tenancy.TenancyApiViewset, basename="tenancy-api")
router.register("client", client.ClientApiViewset, basename="client-api")
router.register("account", accounts.AccountApiViewset, basename="account-api")
router.register(
    "template-email",
    email_templates.EmailTemplateApiViewset,
    basename="template-email-api",
)
router.register(
    "template-notify",
    notification_templates.NotifyTemplateApiViewset,
    basename="template-notify-api",
)
router.register(
    "template-doc",
    document_templates.DocumentTemplateApiViewset,
    basename="template-doc-api",
)


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
    # Templates
    path("templates/", templates_list.template_list_page_view, name="template-list"),
    # Email templates
    path(
        "templates/email/",
        email_templates.template_email_list_page_view,
        name="template-email-list",
    ),
    path(
        "templates/email/create/",
        email_templates.template_email_create_page_view,
        name="template-email-create",
    ),
    re_path(
        f"^templates/email/{INT_PK}/$",
        email_templates.template_email_detail_page_view,
        name="template-email-detail",
    ),
    # Notification templates
    path(
        "templates/notify/",
        notification_templates.template_notify_list_page_view,
        name="template-notify-list",
    ),
    path(
        "templates/notify/create/",
        notification_templates.template_notify_create_page_view,
        name="template-notify-create",
    ),
    re_path(
        f"^templates/notify/{INT_PK}/$",
        notification_templates.template_notify_detail_page_view,
        name="template-notify-detail",
    ),
    # Document templates
    path(
        "templates/doc/",
        document_templates.template_doc_list_page_view,
        name="template-doc-list",
    ),
    path(
        "templates/doc/create/",
        document_templates.template_doc_create_page_view,
        name="template-doc-create",
    ),
    # Custom router urls: we are removing these one-by-one.
    path("cases/", case_router.include()),
    path("", root.root_view, name="case-root"),
]
