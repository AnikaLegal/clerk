"""
Smoke tests for pages that render HTML or React apps.
ie. not JSON API endpoints
"""
from dataclasses import dataclass
from typing import Optional

import pytest
from django.urls import reverse
from factory.django import DjangoModelFactory

from core import factories


@dataclass
class PageTestCase:
    name: str
    is_detail: bool
    factory: Optional[DjangoModelFactory]


PAGE_TEST_CASE = [
    PageTestCase(name="case-list", factory=factories.IssueFactory, is_detail=False),
    PageTestCase(name="case-review", factory=factories.IssueFactory, is_detail=False),
    PageTestCase(name="case-inbox", factory=factories.IssueFactory, is_detail=False),
    PageTestCase(name="case-detail", factory=factories.IssueFactory, is_detail=True),
    PageTestCase(name="case-docs", factory=factories.IssueFactory, is_detail=True),
    PageTestCase(name="case-services", factory=factories.IssueFactory, is_detail=True),
    PageTestCase(name="person-list", factory=factories.PersonFactory, is_detail=False),
    PageTestCase(
        name="person-create", factory=factories.PersonFactory, is_detail=False
    ),
    PageTestCase(name="person-detail", factory=factories.PersonFactory, is_detail=True),
    PageTestCase(
        name="tenancy-detail", factory=factories.TenancyFactory, is_detail=True
    ),
    PageTestCase(name="client-detail", factory=factories.ClientFactory, is_detail=True),
    PageTestCase(name="account-list", factory=factories.UserFactory, is_detail=False),
    PageTestCase(name="account-create", factory=None, is_detail=False),
    PageTestCase(name="account-detail", factory=factories.UserFactory, is_detail=True),
    PageTestCase(name="paralegal-list", factory=factories.UserFactory, is_detail=False),
    PageTestCase(name="template-list", factory=None, is_detail=False),
    PageTestCase(
        name="template-email-list",
        factory=factories.EmailTemplateFactory,
        is_detail=False,
    ),
    PageTestCase(
        name="template-email-create",
        factory=factories.EmailTemplateFactory,
        is_detail=False,
    ),
    PageTestCase(
        name="template-email-detail",
        factory=factories.EmailTemplateFactory,
        is_detail=True,
    ),
    PageTestCase(
        name="template-notify-list",
        factory=factories.NotificationFactory,
        is_detail=False,
    ),
    PageTestCase(
        name="template-notify-create",
        factory=factories.NotificationFactory,
        is_detail=False,
    ),
    PageTestCase(
        name="template-notify-detail",
        factory=factories.NotificationFactory,
        is_detail=True,
    ),
    PageTestCase(name="template-doc-list", factory=None, is_detail=False),
    PageTestCase(name="template-doc-create", factory=None, is_detail=False),
]

TEST_NAMES = [tc.name for tc in PAGE_TEST_CASE]


@pytest.mark.django_db
@pytest.mark.parametrize("test_case", PAGE_TEST_CASE, ids=TEST_NAMES)
def test_case_page_status_code(superuser_client, test_case):
    """
    Ensure URLs return the correct status code.
    """
    instance = test_case.factory() if test_case.factory else None
    if test_case.is_detail:
        assert instance, "A factory is required"
        url = reverse(test_case.name, args=(instance.pk,))
    else:
        url = reverse(test_case.name)

    response = superuser_client.get(url)
    msg = f"URL name {test_case.name} failed, expecting status 200 got {response.status_code}"
    assert response.status_code == 200, msg


EMAIL_PAGE_TEST_CASE = [
    PageTestCase(
        name="case-email-list", factory=factories.EmailFactory, is_detail=False
    ),
    PageTestCase(name="case-email-draft", factory=None, is_detail=False),
    PageTestCase(
        name="case-email-edit", factory=factories.EmailFactory, is_detail=True
    ),
    PageTestCase(
        name="case-email-preview", factory=factories.EmailFactory, is_detail=True
    ),
]

EMAIL_TEST_NAMES = [tc.name for tc in EMAIL_PAGE_TEST_CASE]


@pytest.mark.django_db
@pytest.mark.parametrize("test_case", EMAIL_PAGE_TEST_CASE, ids=EMAIL_TEST_NAMES)
def test_case_email_page_status_code(superuser_client, test_case):
    """
    Ensure URLs return the correct status code for email pages.
    """
    email = None
    issue = factories.IssueFactory()
    if test_case.factory:
        email = test_case.factory(issue=issue)
    if test_case.is_detail:
        assert email, "A factory is required"
        url = reverse(
            test_case.name,
            args=(issue.pk, email.pk),
        )
    else:
        url = reverse(test_case.name, args=(issue.pk,))

    response = superuser_client.get(url)
    msg = f"URL name {test_case.name} failed, expecting status 200 got {response.status_code}"
    assert response.status_code == 200, msg


@pytest.mark.django_db
def test_case_thread_view_page_status_code(superuser_client):
    """
    Ensure URLs return the correct status code for email thread view page.
    """
    issue = factories.IssueFactory()
    factories.EmailFactory(issue=issue, subject="foo")
    url = reverse("case-email-thread", args=(issue.pk, "foo"))
    response = superuser_client.get(url)
    msg = f"URL name case-email-thread failed, expecting status 200 got {response.status_code}"
    assert response.status_code == 200, msg
