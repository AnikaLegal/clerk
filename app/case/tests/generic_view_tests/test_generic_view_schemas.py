"""
Tests to check openapi schema validation for generic view test cases.
TODO: test create and update generic views.
"""
import uuid

import pytest
from rest_framework.test import APIClient
from rest_framework.reverse import reverse

from accounts.models import CaseGroups
from case.tests.generic_view_tests.generic_view_test_cases import (
    APIViewTestCase,
    GENERIC_API_TEST_CASES,
)
from conftest import schema_tester


TEST_GROUPS = [
    CaseGroups.ADMIN,
    CaseGroups.COORDINATOR,
    CaseGroups.PARALEGAL,
    CaseGroups.LAWYER,
]


@pytest.mark.django_db
@pytest.mark.parametrize("test_case", GENERIC_API_TEST_CASES)
def test_generic_list_view_schema(
    superuser_client: APIClient, test_case: APIViewTestCase
) -> None:
    """
    Ensure that a given view's API list view matches the schema.
    """
    # Create an instance of the model
    instance = test_case.factory.create()

    # Try view a list of instances
    list_view_name = f"{test_case.base_view_name}-list"
    url = reverse(list_view_name)
    response = superuser_client.get(url)

    # Check results
    assert response.status_code == 200, response.json()
    assert len(response.json()) == 1
    if isinstance(instance.id, uuid.UUID):
        assert response.json()[0]["id"] == str(instance.id)
    else:
        assert response.json()[0]["id"] == instance.id
    schema_tester.validate_response(response=response)


@pytest.mark.django_db
@pytest.mark.parametrize("test_case", GENERIC_API_TEST_CASES)
def test_generic_detail_view_schema(
    superuser_client: APIClient, test_case: APIViewTestCase
) -> None:
    """
    Ensure that a given view's API detail view matches the schema.
    """
    # Create an instance of the model
    instance = test_case.factory.create()

    # Try view a single instance
    detail_view_name = f"{test_case.base_view_name}-detail"
    url = reverse(detail_view_name, kwargs=dict(pk=instance.pk))
    response = superuser_client.get(url)

    # Check results
    assert response.status_code == 200, response.json()
    if isinstance(instance.id, uuid.UUID):
        assert response.json()["id"] == str(instance.id)
    else:
        assert response.json()["id"] == instance.id
    schema_tester.validate_response(response=response)


@pytest.mark.django_db
@pytest.mark.parametrize("test_case", GENERIC_API_TEST_CASES)
def test_generic_delete_view_schema(
    superuser_client: APIClient, test_case: APIViewTestCase
) -> None:
    """
    Ensure that a given view's API delete view matches the schema.
    """
    Model = test_case.factory._meta.model

    # Create an instance of the model
    instance = test_case.factory.create()
    assert Model.objects.count() == 1

    # Try view a single instance
    detail_view_name = f"{test_case.base_view_name}-detail"
    url = reverse(detail_view_name, kwargs=dict(pk=instance.pk))
    response = superuser_client.delete(url)

    # Check results
    assert response.status_code == 204, response.json()
    assert Model.objects.count() == 0
    schema_tester.validate_response(response=response)
