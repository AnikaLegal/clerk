"""
Smoke tests for HTML pages.
"""
from dataclasses import dataclass

import pytest
from django.urls import reverse
from factory.django import DjangoModelFactory

from core import factories


@dataclass
class PageTestCase:
    name: str
    is_detail: bool
    factory: DjangoModelFactory


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
    PageTestCase(name="account-create", factory=factories.UserFactory, is_detail=False),
    PageTestCase(name="account-detail", factory=factories.UserFactory, is_detail=True),
    PageTestCase(name="paralegal-list", factory=factories.UserFactory, is_detail=False),
]

TEST_NAMES = [tc.name for tc in PAGE_TEST_CASE]


@pytest.mark.django_db
@pytest.mark.parametrize("test_case", PAGE_TEST_CASE, ids=TEST_NAMES)
def test_case_page_status_code(superuser_client, test_case):
    """
    Ensure URLs return the correct status code.
    """
    instance = test_case.factory()
    if test_case.is_detail:
        url = reverse(test_case.name, args=(instance.pk,))
    else:
        url = reverse(test_case.name)

    response = superuser_client.get(url)
    msg = f"URL name {test_case.name} failed, expecting status 200 got {response.status_code}"
    assert response.status_code == 200, msg
