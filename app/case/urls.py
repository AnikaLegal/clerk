from django.urls import path, re_path

from . import views

UUID_PARAM = r"(?P<pk>[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-4[0-9a-fA-F]{3}-[89abAB][0-9a-fA-F]{3}-[0-9a-fA-F]{12})"
INT_PK_PARAM = r"(?P<pk>[0-9]+)"
FORM_SLUG_PARAM = r"(?P<form_slug>[\-\w]+)"


urlpatterns = [
    # Paralegals
    path("paralegals/", views.paralegal.paralegal_list_view, name="paralegal-list"),
    # Person
    re_path(
        fr"^person/{INT_PK_PARAM}/{FORM_SLUG_PARAM}?/?$",
        views.client.person_detail_view,
        name="person-detail",
    ),
    # Tenancy
    re_path(
        fr"^tenancy/{INT_PK_PARAM}/{FORM_SLUG_PARAM}?/?$",
        views.client.tenancy_detail_view,
        name="tenancy-detail",
    ),
    # Client
    re_path(
        fr"^client/{UUID_PARAM}/{FORM_SLUG_PARAM}?/?$",
        views.client.client_detail_view,
        name="client-detail",
    ),
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
        fr"^cases/{UUID_PARAM}/{FORM_SLUG_PARAM}?/?$",
        views.case.case_detail_view,
        name="case-detail",
    ),
    path("not-allowed/", views.case.not_allowed_view, name="case-not-allowed"),
    path("", views.case.root_view, name="case-root"),
]
