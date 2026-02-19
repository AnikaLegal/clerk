import pytest
from unittest.mock import patch
from rest_framework.test import APIClient
from rest_framework.reverse import reverse

from accounts.models import User
from core.factories import UserFactory
from microsoft.service import MicrosoftUserPermissions


@pytest.mark.django_db
@patch("microsoft.tasks._invite_user_if_not_exists")
def test_create_account_view(
    mock_invite_user_if_not_exists,
    superuser_client: APIClient,
):
    assert User.objects.count() == 1
    url = reverse("account-api-list")
    data = {
        "first_name": "Charlie",
        "last_name": "Brown",
        "email": "charlie.brown@anikalegal.com",
        "groups": ["Paralegal"],
    }
    response = superuser_client.post(url, data, format="json")
    assert response.status_code == 201, response.json()
    assert response.json()["email"] == "charlie.brown@anikalegal.com"
    assert User.objects.count() == 2
    user = User.objects.get(email="charlie.brown@anikalegal.com")
    mock_invite_user_if_not_exists.assert_called_with(user)
    assert list(user.groups.values_list("name", flat=True)) == ["Paralegal"]
    assert user.ms_account_created_at is not None


@pytest.mark.django_db
def test_issue_accounts_list_api__name_filter(superuser_client: APIClient):
    charlie = UserFactory(first_name="Charlie", last_name="Brown")
    sally = UserFactory(first_name="Sally", last_name="Brown")
    lucy = UserFactory(first_name="Lucy", last_name="Van Pelt")
    url = reverse("account-api-list")

    # Make sure we don't match the superuser.
    superuser = User.objects.get(is_superuser=True)
    superuser.first_name = "Peppermint"
    superuser.last_name = "Patty"
    superuser.save()

    response = superuser_client.get(url, {"name": "Charlie"})
    assert response.status_code == 200, response.json()
    data = response.json()
    assert len(data["results"]) == 1
    assert data["results"][0]["email"] == charlie.email

    response = superuser_client.get(url, {"name": "Van Pelt"})
    assert response.status_code == 200, response.json()
    data = response.json()
    assert len(data["results"]) == 1
    assert data["results"][0]["email"] == lucy.email

    response = superuser_client.get(url, {"name": "Brown"})
    assert response.status_code == 200, response.json()
    data = response.json()
    assert len(data["results"]) == 2
    emails = {result["email"] for result in data["results"]}
    assert emails == {charlie.email, sally.email}


@pytest.mark.django_db
def test_issue_accounts_list_api__group_filter(
    superuser_client: APIClient, paralegal_group, coordinator_group
):
    paralegal = UserFactory()
    paralegal.groups.add(paralegal_group)

    coordinator = UserFactory()
    coordinator.groups.add(coordinator_group)

    url = reverse("account-api-list")

    response = superuser_client.get(url, {"group": "Paralegal"})
    assert response.status_code == 200, response.json()
    data = response.json()
    assert len(data["results"]) == 1
    assert data["results"][0]["email"] == paralegal.email

    response = superuser_client.get(url, {"group": "Coordinator"})
    assert response.status_code == 200, response.json()
    data = response.json()
    assert len(data["results"]) == 1
    assert data["results"][0]["email"] == coordinator.email


@pytest.mark.django_db
def test_issue_accounts_list_api__is_active_filter(superuser_client: APIClient):
    active_user = UserFactory(is_active=True)
    inactive_user = UserFactory(is_active=False)
    url = reverse("account-api-list")

    assert User.objects.filter(is_active=True).count() == 2  # includes superuser
    assert User.objects.filter(is_active=False).count() == 1

    response = superuser_client.get(url, {"is_active": "true"})
    assert response.status_code == 200, response.json()
    data = response.json()
    assert len(data["results"]) == 2, data["results"]
    emails = {result["email"] for result in data["results"]}
    assert active_user.email in emails

    response = superuser_client.get(url, {"is_active": "false"})
    assert response.status_code == 200, response.json()
    data = response.json()
    assert len(data["results"]) == 1, data["results"]
    assert data["results"][0]["email"] == inactive_user.email


@pytest.mark.django_db
def test_create_account_view__with_external_email(superuser_client: APIClient):
    assert User.objects.count() == 1
    url = reverse("account-api-list")
    data = {
        "first_name": "Charlie",
        "last_name": "Brown",
        "email": "charlie.brown@example.com",
        "groups": ["Paralegal"],
    }
    response = superuser_client.post(url, data, format="json")
    assert response.status_code == 400, response.json()


@pytest.mark.django_db
@patch("case.views.accounts.get_user_permissions")
def test_get_account_permissions_view(
    mock_get_user_permissions, superuser_client: APIClient
):
    user = UserFactory()
    url = reverse("account-api-perms", args=(user.pk,))
    mock_get_user_permissions.return_value = MicrosoftUserPermissions(
        access_level="NO_ACCESS",
        issues_with_access=[],
        issues_without_access=[],
    )

    response = superuser_client.get(url)
    assert response.status_code == 200
    assert response.json() == {
        "access_level": "NO_ACCESS",
        "issues_with_access": [],
        "issues_without_access": [],
    }


@pytest.mark.django_db
@patch("case.views.accounts.reset_ms_access")
@patch("case.views.accounts.get_user_permissions")
def test_resync_account_permissions_view(
    mock_get_user_permissions, mock_reset_ms_access, superuser_client: APIClient
):
    user = UserFactory()
    url = reverse("account-api-perms-resync", args=(user.pk,))
    mock_get_user_permissions.return_value = MicrosoftUserPermissions(
        access_level="NO_ACCESS",
        issues_with_access=[],
        issues_without_access=[],
    )
    response = superuser_client.post(url)
    assert response.status_code == 200
    mock_reset_ms_access.assert_called_with(user)
    resp_data = response.json()
    assert resp_data["account"]["id"] == user.pk
    assert resp_data["permissions"] == {
        "access_level": "NO_ACCESS",
        "issues_with_access": [],
        "issues_without_access": [],
    }
