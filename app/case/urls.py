from django.urls import path, re_path

from . import views

UUID_PARAM = r"(?P<pk>[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-4[0-9a-fA-F]{3}-[89abAB][0-9a-fA-F]{3}-[0-9a-fA-F]{12})"
INT_PK_PARAM = r"(?P<pk>[0-9]+)"
FORM_SLUG_PARAM = r"(?P<form_slug>[\-\w]+)"

from .views.client import router as client_router
from .views.paralegal import router as paralegal_router
from .views.person import router as person_router
from .views.tenancy import router as tenancy_router
from .views.case import root_view, not_allowed_view

urlpatterns = [
    # Paralegals
    path("paralegals/", paralegal_router.urls()),
    path("person/", person_router.urls()),
    path("tenancy/", tenancy_router.urls()),
    path("client/", client_router.urls()),
    # Accounts
    path("accounts/", views.accounts.account_list_view, name="account-list"),
    re_path(
        fr"^accounts/{INT_PK_PARAM}/{FORM_SLUG_PARAM}?/?$",
        views.accounts.account_detail_view,
        name="account-detail",
    ),
    # Cases
    path("cases/", views.case.case_list_view, name="case-list"),
    path("cases/inbox/", views.case.case_inbox_view, name="case-inbox"),
    path("cases/review/", views.case.case_review_view, name="case-review"),
    re_path(
        fr"^cases/{UUID_PARAM}/email/$",
        views.case.case_detail_email_view,
        name="case-detail-email",
    ),
    re_path(
        fr"^cases/{UUID_PARAM}/email/draft/$",
        views.case.case_detail_email_draft_view,
        name="case-detail-email-draft",
    ),
    re_path(
        fr"^cases/{UUID_PARAM}/email/draft/(?P<email_pk>[0-9]+)/$",
        views.case.case_detail_email_draft_edit_view,
        name="case-detail-email-draft-edit",
    ),
    re_path(
        fr"^cases/{UUID_PARAM}/email/draft/(?P<email_pk>[0-9]+)/send/$",
        views.case.case_detail_email_draft_send_view,
        name="case-detail-email-draft-send",
    ),
    re_path(
        fr"^cases/{UUID_PARAM}/email/draft/(?P<email_pk>[0-9]+)/attachment/(?P<attach_pk>[0-9]+)/$",
        views.case.case_detail_email_draft_edit_view,
        name="case-detail-email-attachment",
    ),
    re_path(
        fr"^cases/{UUID_PARAM}/{FORM_SLUG_PARAM}?/?$",
        views.case.case_detail_view,
        name="case-detail",
    ),
    path("not-allowed/", not_allowed_view, name="case-not-allowed"),
    path("", root_view, name="case-root"),
]
