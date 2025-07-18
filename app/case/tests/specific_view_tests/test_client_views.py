import pytest
from conftest import schema_tester
from core.factories import ClientFactory, IssueFactory
from rest_framework.reverse import reverse
from rest_framework.test import APIClient


@pytest.mark.django_db
def test_client_list_api(superuser_client: APIClient):
    instance_1 = ClientFactory()
    instance_2 = ClientFactory()

    url = reverse("client-api-list")
    response = superuser_client.get(url)

    assert response.status_code == 200, response.json()
    data = response.json()

    assert data["current"] == 1
    assert data["item_count"] == 2
    assert data["page_count"] == 1
    assert data["next"] is None
    assert data["prev"] is None

    results = data["results"]
    assert len(results) == 2
    assert set(x["id"] for x in results) == {str(instance_1.pk), str(instance_2.pk)}

    schema_tester.validate_response(response=response)


@pytest.mark.django_db
def test_client_list_api__q_filter(superuser_client: APIClient):
    instance_1 = ClientFactory(first_name="Charlie", last_name="Brown")
    instance_2 = ClientFactory(first_name="Sally", last_name="Brown")
    url = reverse("client-api-list")

    # Empty search parameter.
    response = superuser_client.get(url, {"q": ""})
    assert response.status_code == 400

    # No search results.
    response = superuser_client.get(url, {"q": "MISS"})
    assert response.status_code == 200
    resp_data = response.json()
    assert resp_data["item_count"] == 0
    results = resp_data["results"]
    assert len(results) == 0

    # One search result.
    response = superuser_client.get(url, {"q": "Charlie"})
    assert response.status_code == 200
    resp_data = response.json()
    assert resp_data["item_count"] == 1
    results = resp_data["results"]
    assert len(results) == 1
    assert results[0]["id"] == str(instance_1.pk)
    schema_tester.validate_response(response=response)

    # Two search results.
    response = superuser_client.get(url, {"q": "Brown"})
    assert response.status_code == 200
    resp_data = response.json()
    assert resp_data["item_count"] == 2
    results = resp_data["results"]
    assert len(results) == 2
    assert set(x["id"] for x in results) == {str(instance_1.pk), str(instance_2.pk)}

    schema_tester.validate_response(response=response)


@pytest.mark.django_db
def test_client_retrieve_api(superuser_client: APIClient):
    instance = ClientFactory()
    url = reverse("client-api-detail", args=(instance.pk,))
    response = superuser_client.get(url)

    assert response.status_code == 200, response.json()
    data = response.json()
    assert data["id"] == str(instance.pk)

    schema_tester.validate_response(response=response)


@pytest.mark.django_db
def test_client_update_api(superuser_client: APIClient):
    instance = ClientFactory()
    url = reverse("client-api-detail", args=(instance.pk,))
    data = {
        "first_name": "Charlie",
        "last_name": "Brown",
        "email": "charlie.brown@example.com",
    }
    response = superuser_client.patch(url, data=data, format="json")
    assert response.status_code == 200, response.json()

    instance.refresh_from_db()
    assert instance.first_name == "Charlie"
    assert instance.last_name == "Brown"
    assert instance.email == "charlie.brown@example.com"

    data = response.json()
    assert data["first_name"] == instance.first_name
    assert data["last_name"] == instance.last_name
    assert data["email"] == instance.email

    schema_tester.validate_response(response=response)


#
# TODO: test results
#
@pytest.mark.django_db
@pytest.mark.parametrize(
    "test_user, user_name, is_assigned, expected_status, expected_count",
    [
        ("unassigned_user", "unprivileged_user", False, 403, None),
        ("assigned_user", "unprivileged_user", True, 403, None),
        ("unassigned_paralegal", "paralegal_user", False, 200, 0),
        ("assigned_paralegal", "paralegal_user", True, 200, 1),
        ("unassigned_coordinator", "coordinator_user", False, 200, 1),
        ("assigned_coordinator", "coordinator_user", True, 200, 1),
    ],
)
def test_client_api_list_perms(
    test_user: str,
    user_name: str,
    is_assigned: bool,
    expected_status: int,
    expected_count: int,
    user_client,
    request,
):
    """
    Test list API perms for different users.
    """
    user = request.getfixturevalue(user_name)
    issue = IssueFactory()
    if is_assigned:
        issue.paralegal = user
        issue.save()

    url = reverse("client-api-list")
    response = user_client.get(url)

    assert response.status_code == expected_status

    if expected_count is not None:
        data = response.json()
        assert data["item_count"] == expected_count
        results = data["results"]
        assert len(results) == expected_count


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
def test_client_api_retrieve_perms(
    test_user: str,
    user_name: str,
    is_assigned: bool,
    expected_status: int,
    user_client,
    request,
):
    """
    Test display API perms for different users.
    """
    user = request.getfixturevalue(user_name)
    issue = IssueFactory()
    if is_assigned:
        issue.paralegal = user
        issue.save()

    url = reverse("client-api-detail", args=(issue.client.pk,))
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
def test_client_api_update_perms(
    test_user: str,
    user_name: str,
    is_assigned: bool,
    expected_status: int,
    user_client,
    request,
):
    """
    Test update API perms for different users.
    """
    user = request.getfixturevalue(user_name)
    issue = IssueFactory()
    if is_assigned:
        issue.paralegal = user
        issue.save()

    data = {
        "last_name": "Brown",
    }
    url = reverse("client-api-detail", args=(issue.client.pk,))
    response = user_client.patch(url, data=data, format="json")

    assert response.status_code == expected_status
