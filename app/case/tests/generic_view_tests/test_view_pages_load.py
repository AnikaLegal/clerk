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
from emails.models import EmailTemplate


@dataclass
class PageTestCase:
    name: str
    is_detail: bool
    factory: Optional[DjangoModelFactory]


BuildEmailTemplate = lambda: EmailTemplate.objects.create(
    name="Test", topic="GENERAL", text="Hello", subject="World"
)

PAGE_TEST_CASE = [
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
        name="template-email-list", factory=BuildEmailTemplate, is_detail=False
    ),
    PageTestCase(
        name="template-email-create", factory=BuildEmailTemplate, is_detail=False
    ),
    PageTestCase(
        name="template-email-detail", factory=BuildEmailTemplate, is_detail=True
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