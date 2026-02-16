from enum import Enum

import pytest
from conftest import schema_tester
from core.factories import IssueFactory, TenancyFactory
from rest_framework.reverse import reverse
from rest_framework.test import APIClient


class AssignedAs(Enum):
    NONE = 1
    PARALEGAL = 2
    LAWYER = 3


@pytest.mark.django_db
def test_tenancy_retrieve_api(superuser_client: APIClient):
    instance = TenancyFactory()
    url = reverse("tenancy-api-detail", args=(instance.pk,))
    response = superuser_client.get(url)

    assert response.status_code == 200, response.json()
    data = response.json()
    assert data["id"] == instance.pk

    schema_tester.validate_response(response=response)


@pytest.mark.django_db
def test_tenancy_update_api(superuser_client: APIClient):
    instance = TenancyFactory(
        address="123 Fake St",
        suburb="Noburg",
        postcode="1234",
    )
    url = reverse("tenancy-api-detail", args=(instance.pk,))
    data = {
        "address": "999 Fake Street",
        "suburb": "Yesburg",
        "postcode": "4321",
    }
    response = superuser_client.patch(url, data=data, format="json")
    assert response.status_code == 200, response.json()

    instance.refresh_from_db()
    assert instance.address == "999 Fake Street"
    assert instance.suburb == "Yesburg"
    assert instance.postcode == "4321"

    data = response.json()
    assert data["address"] == instance.address
    assert data["suburb"] == instance.suburb
    assert data["postcode"] == instance.postcode

    schema_tester.validate_response(response=response)


@pytest.mark.django_db
@pytest.mark.parametrize(
    "user_name, assigned_as, expected_status",
    [
        ("unprivileged_user", AssignedAs.NONE, 403),
        ("unprivileged_user", AssignedAs.PARALEGAL, 403),
        ("unprivileged_user", AssignedAs.LAWYER, 403),
        ("paralegal_user", AssignedAs.NONE, 403),
        ("paralegal_user", AssignedAs.PARALEGAL, 200),
        ("paralegal_user", AssignedAs.LAWYER, 403),
        ("lawyer_user", AssignedAs.NONE, 403),
        ("lawyer_user", AssignedAs.PARALEGAL, 200),
        ("lawyer_user", AssignedAs.LAWYER, 200),
        ("coordinator_user", AssignedAs.NONE, 200),
        ("coordinator_user", AssignedAs.PARALEGAL, 200),
        ("coordinator_user", AssignedAs.LAWYER, 200),
        ("admin_user", AssignedAs.NONE, 200),
        ("admin_user", AssignedAs.PARALEGAL, 200),
        ("admin_user", AssignedAs.LAWYER, 200),
    ],
)
def test_tenancy_api_retrieve_perms(
    user_name: str,
    assigned_as: AssignedAs,
    expected_status: int,
    user_client,
    request,
):
    """
    Test creation of a tenancy via the API as different users.
    """
    user = request.getfixturevalue(user_name)
    issue = IssueFactory()
    if assigned_as == AssignedAs.PARALEGAL:
        issue.paralegal = user
        issue.save()
    elif assigned_as == AssignedAs.LAWYER:
        issue.lawyer = user
        issue.save()

    url = reverse("tenancy-api-detail", args=(issue.tenancy.pk,))
    response = user_client.get(url)

    assert response.status_code == expected_status


@pytest.mark.django_db
@pytest.mark.parametrize(
    "user_name, assigned_as, expected_status",
    [
        ("unprivileged_user", AssignedAs.NONE, 403),
        ("unprivileged_user", AssignedAs.PARALEGAL, 403),
        ("unprivileged_user", AssignedAs.LAWYER, 403),
        ("paralegal_user", AssignedAs.NONE, 403),
        ("paralegal_user", AssignedAs.PARALEGAL, 200),
        ("paralegal_user", AssignedAs.LAWYER, 403),
        ("lawyer_user", AssignedAs.NONE, 403),
        ("lawyer_user", AssignedAs.PARALEGAL, 200),
        ("lawyer_user", AssignedAs.LAWYER, 200),
        ("coordinator_user", AssignedAs.NONE, 200),
        ("coordinator_user", AssignedAs.PARALEGAL, 200),
        ("coordinator_user", AssignedAs.LAWYER, 200),
        ("admin_user", AssignedAs.NONE, 200),
        ("admin_user", AssignedAs.PARALEGAL, 200),
        ("admin_user", AssignedAs.LAWYER, 200),
    ],
)
def test_tenancy_api_update_perms(
    user_name: str,
    assigned_as: AssignedAs,
    expected_status: int,
    user_client,
    request,
):
    """
    Test creation of a tenancy via the API as different users.
    """
    user = request.getfixturevalue(user_name)
    issue = IssueFactory()
    if assigned_as == AssignedAs.PARALEGAL:
        issue.paralegal = user
        issue.save()
    elif assigned_as == AssignedAs.LAWYER:
        issue.lawyer = user
        issue.save()

    data = {
        "address": "123 Fake St",
    }
    url = reverse("tenancy-api-detail", args=(issue.tenancy.pk,))
    response = user_client.patch(url, data=data, format="json")

    assert response.status_code == expected_status
