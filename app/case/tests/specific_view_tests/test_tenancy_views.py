import pytest
from conftest import schema_tester
from core.factories import TenancyFactory, IssueFactory
from rest_framework.reverse import reverse
from rest_framework.test import APIClient


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
    "test_user, user_name, is_assigned, expected_status",
    [
        ("unassigned_user", "unprivileged_user", False, 403),
        ("assigned_user", "unprivileged_user", True, 403),
        ("unassigned_paralegal", "paralegal_user", False, 403),
        ("assigned_paralegal", "paralegal_user", True, 200),
        ("unassigned_coordinator", "coordinator_user", False, 200),
        ("assigned_coordinator", "coordinator_user", True, 200),
    ],
)
def test_tenancy_api_retrieve_perms(
    test_user: str,
    user_name: str,
    is_assigned: bool,
    expected_status: int,
    user_client,
    request,
):
    """
    Test creation of a tenancy via the API as different users.
    """
    user = request.getfixturevalue(user_name)
    issue = IssueFactory()
    if is_assigned:
        issue.paralegal = user
        issue.save()

    url = reverse("tenancy-api-detail", args=(issue.tenancy.pk,))
    response = user_client.get(url)

    assert response.status_code == expected_status


@pytest.mark.django_db
@pytest.mark.parametrize(
    "test_user, user_name, is_assigned, expected_status",
    [
        ("unassigned_user", "unprivileged_user", False, 403),
        ("assigned_user", "unprivileged_user", True, 403),
        ("unassigned_paralegal", "paralegal_user", False, 403),
        ("assigned_paralegal", "paralegal_user", True, 200),
        ("unassigned_coordinator", "coordinator_user", False, 200),
        ("assigned_coordinator", "coordinator_user", True, 200),
    ],
)
def test_tenancy_api_update_perms(
    test_user: str,
    user_name: str,
    is_assigned: bool,
    expected_status: int,
    user_client,
    request,
):
    """
    Test creation of a tenancy via the API as different users.
    """
    user = request.getfixturevalue(user_name)
    issue = IssueFactory()
    if is_assigned:
        issue.paralegal = user
        issue.save()

    data = {
        "address": "123 Fake St",
    }
    url = reverse("tenancy-api-detail", args=(issue.tenancy.pk,))
    response = user_client.patch(url, data=data, format="json")

    assert response.status_code == expected_status
