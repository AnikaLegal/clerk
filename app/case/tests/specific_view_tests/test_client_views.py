import pytest
from rest_framework.test import APIClient
from rest_framework.reverse import reverse

from accounts.models import User
from case.middleware import annotate_group_access
from core.factories import ClientFactory, IssueFactory
from core.models import Client
from conftest import schema_tester


@pytest.mark.django_db
def test_client_list_view__with_no_access(user_client: APIClient, user: User):
    """
    Unprivileged users are forbidden to list clients.
    """
    ClientFactory()  # There's an issue but the user can't see it
    annotate_group_access(user)
    url = reverse("client-api-list")
    response = user_client.get(url)
    assert response.status_code == 403


@pytest.mark.django_db
def test_client_list_view__as_paralegal_with_no_access(
    user_client: APIClient,
    user: User,
    paralegal_group,
):
    """
    Paralegal users can list clients but no results because they're not assigned
    """
    ClientFactory()  # There's a client but the user can't see it
    user.groups.set([paralegal_group])
    annotate_group_access(user)
    url = reverse("client-api-list")
    response = user_client.get(url)
    assert response.status_code == 200
    assert response.json() == {
        "current": 1,
        "item_count": 0,
        "next": None,
        "page_count": 1,
        "prev": None,
        "results": [],
    }
    schema_tester.validate_response(response=response)


@pytest.mark.django_db
def test_client_list_view__as_paralegal_with_access(
    user_client: APIClient,
    user: User,
    paralegal_group,
):
    """
    Paralegal users can list client of cases to which they're assigned.
    """
    issue = IssueFactory(paralegal=user)
    IssueFactory()  # There's an issue but the user can't see it

    user.groups.set([paralegal_group])
    annotate_group_access(user)
    url = reverse("client-api-list")
    response = user_client.get(url)
    assert response.status_code == 200
    resp_data = response.json()

    assert resp_data["current"] == 1
    assert resp_data["item_count"] == 1
    assert resp_data["page_count"] == 1
    assert resp_data["next"] is None
    assert resp_data["prev"] is None
    results = resp_data["results"]
    assert len(results) == 1
    assert results[0]["id"] == str(issue.client.pk)
    schema_tester.validate_response(response=response)


@pytest.mark.django_db
def test_client_list_view__as_coordinator(
    user_client: APIClient,
    user: User,
    coordinator_group,
):
    """
    Coordinator users can list clients.
    """
    client_a = ClientFactory()
    client_b = ClientFactory()

    user.groups.set([coordinator_group])
    annotate_group_access(user)
    url = reverse("client-api-list")
    response = user_client.get(url)
    assert response.status_code == 200
    resp_data = response.json()

    assert resp_data["current"] == 1
    assert resp_data["item_count"] == 2
    assert resp_data["page_count"] == 1
    assert resp_data["next"] is None
    assert resp_data["prev"] is None
    results = resp_data["results"]
    assert len(results) == 2
    assert set(r["id"] for r in results) == {str(client_a.pk), str(client_b.pk)}
    schema_tester.validate_response(response=response)


@pytest.mark.django_db
def test_client_list_view__search(superuser_client: APIClient):
    client_a = ClientFactory(first_name="John", last_name="Smith")
    client_b = ClientFactory(first_name="Jane", last_name="Smith")
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
    response = superuser_client.get(url, {"q": "John"})
    assert response.status_code == 200
    resp_data = response.json()
    assert resp_data["item_count"] == 1
    results = resp_data["results"]
    assert len(results) == 1
    assert results[0]["id"] == str(client_a.pk)
    schema_tester.validate_response(response=response)

    # Two search results.
    response = superuser_client.get(url, {"q": "Smith"})
    assert response.status_code == 200
    resp_data = response.json()
    assert resp_data["item_count"] == 2
    results = resp_data["results"]
    assert len(results) == 2
    assert set(x["id"] for x in results) == {str(client_a.pk), str(client_b.pk)}

    schema_tester.validate_response(response=response)


@pytest.mark.django_db
def test_client_detail_view__as_paralegal(
    user_client: APIClient,
    user: User,
    paralegal_group,
):
    """
    Paralegal users can only display client of cases to which they're assigned.
    """
    issue = IssueFactory()

    user.groups.set([paralegal_group])
    annotate_group_access(user)

    # Paralegals are not allowed to get the client details when they're not
    # assigned to the issue.
    url = reverse("client-api-detail", args=(issue.client.pk,))
    response = user_client.get(url)
    assert response.status_code == 403

    # User can display the client now they're assigned.
    issue.paralegal = user
    issue.save()

    response = user_client.get(url)
    assert response.status_code == 200
    resp_data = response.json()
    assert resp_data["id"] == str(issue.client.pk)

    schema_tester.validate_response(response=response)


@pytest.mark.django_db
def test_case_update_view_permissions(
    user_client: APIClient,
    user: User,
    paralegal_group,
    coordinator_group,
):
    """
    Paralegal users can only update client of cases to which they're assigned.
    Coordinator users can update any clients.
    """
    client = ClientFactory(first_name="John")
    issue = IssueFactory(client=client)
    url = reverse("client-api-detail", args=(client.pk,))
    data = {"first_name": "Jane"}

    # Paralegal user.
    user.groups.set([paralegal_group])
    annotate_group_access(user)
    response = user_client.patch(url, data=data, format="json")
    assert response.status_code == 403

    # Assigned paralegal user.
    issue.paralegal = user
    issue.save()

    response = user_client.patch(url, data=data, format="json")
    assert response.status_code == 200

    # Coordinator user.
    client = ClientFactory(first_name="John")
    url = reverse("client-api-detail", args=(client.pk,))

    user.groups.set([coordinator_group])
    annotate_group_access(user)
    response = user_client.patch(url, data=data, format="json")
    assert response.status_code == 200


@pytest.mark.django_db
def test_client_update_view(superuser_client: APIClient):
    client = ClientFactory(first_name="John")
    issue = IssueFactory(client=client)
    url = reverse("client-api-detail", args=(client.pk,))

    response = superuser_client.patch(url, data={"first_name": "Jane"}, format="json")
    assert response.status_code == 200
    client.refresh_from_db()
    assert client.first_name == "Jane"

    schema_tester.validate_response(response=response)


@pytest.mark.django_db
def test_client_create_view_permissions(
    user_client: APIClient,
    user: User,
    paralegal_group,
    coordinator_group,
):
    """
    Paralegal users can't create clients. Coordinator users can create clients.
    """
    url = reverse("client-api-list")
    data = {
        "first_name": "John",
        "last_name": "Smith",
        "email": "john.smith@example.com",
    }

    # Paralegal user.
    user.groups.set([paralegal_group])
    annotate_group_access(user)
    response = user_client.post(url, data=data, format="json")
    assert response.status_code == 403

    # Coordinator user.
    user.groups.set([coordinator_group])
    annotate_group_access(user)
    response = user_client.post(url, data=data, format="json")
    assert response.status_code == 201


@pytest.mark.django_db
def test_client_create_view(superuser_client: APIClient):
    url = reverse("client-api-list")
    data = {
        "first_name": "John",
        "last_name": "Smith",
        "email": "john.smith@example.com",
    }

    response = superuser_client.post(url, data=data, format="json")
    assert response.status_code == 201

    client = Client.objects.get()
    assert client.first_name == "John"
    assert client.last_name == "Smith"
    assert client.email == "john.smith@example.com"

    schema_tester.validate_response(response=response)
