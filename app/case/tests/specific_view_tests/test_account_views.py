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
        "first_name": "Jane",
        "last_name": "Doe",
        "email": "jane.doe@anikalegal.com",
        "username": "jane.doe@anikalegal.com",
    }
    response = superuser_client.post(url, data, format="json")
    assert response.status_code == 201, response.json()
    assert response.json()["username"] == "jane.doe@anikalegal.com"
    assert User.objects.count() == 2
    user = User.objects.get(email="jane.doe@anikalegal.com")
    mock_invite_user_if_not_exists.assert_called_with(user)
    assert list(user.groups.values_list("name", flat=True)) == ["Paralegal"]
    assert user.ms_account_created_at is not None


@pytest.mark.django_db
def test_create_account_view__with_external_email(superuser_client: APIClient):
    assert User.objects.count() == 1
    url = reverse("account-api-list")
    data = {
        "first_name": "Jane",
        "last_name": "Doe",
        "email": "jane.doe@gmail.com",
        "username": "jane.doe@gmail.com",
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
        has_coordinator_perms=False,
        paralegal_perm_issues=[],
        paralegal_perm_missing_issues=[],
    )

    response = superuser_client.get(url)
    assert response.status_code == 200
    assert response.json() == {
        "has_coordinator_perms": False,
        "paralegal_perm_issues": [],
        "paralegal_perm_missing_issues": [],
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
        has_coordinator_perms=False,
        paralegal_perm_issues=[],
        paralegal_perm_missing_issues=[],
    )
    response = superuser_client.post(url)
    assert response.status_code == 200
    mock_reset_ms_access.assert_called_with(user)
    resp_data = response.json()
    assert resp_data["account"]["id"] == user.pk
    assert resp_data["permissions"] == {
        "has_coordinator_perms": False,
        "paralegal_perm_issues": [],
        "paralegal_perm_missing_issues": [],
    }


@pytest.mark.django_db
@patch("case.views.accounts.reset_ms_access")
@patch("case.views.accounts.get_user_permissions")
def test_promote_account_permissions_view__as_paralegal(
    mock_get_user_permissions,
    mock_reset_ms_access,
    superuser_client: APIClient,
    paralegal_group,
    coordinator_group,
):
    user = UserFactory()
    user.groups.set([paralegal_group])
    url = reverse("account-api-perms-promote", args=(user.pk,))
    mock_get_user_permissions.return_value = MicrosoftUserPermissions(
        has_coordinator_perms=False,
        paralegal_perm_issues=[],
        paralegal_perm_missing_issues=[],
    )
    response = superuser_client.post(url)
    assert response.status_code == 200
    mock_reset_ms_access.assert_not_called()
    resp_data = response.json()
    assert resp_data["account"]["id"] == user.pk
    assert resp_data["permissions"] == {
        "has_coordinator_perms": False,
        "paralegal_perm_issues": [],
        "paralegal_perm_missing_issues": [],
    }
    assert set(user.groups.all()) == {paralegal_group, coordinator_group}


@pytest.mark.django_db
@patch("case.views.accounts.reset_ms_access")
@patch("case.views.accounts.get_user_permissions")
def test_promote_account_permissions_view__with_no_group(
    mock_get_user_permissions,
    mock_reset_ms_access,
    superuser_client: APIClient,
    paralegal_group,
):
    user = UserFactory()
    user.groups.set([])
    url = reverse("account-api-perms-promote", args=(user.pk,))
    mock_get_user_permissions.return_value = MicrosoftUserPermissions(
        has_coordinator_perms=False,
        paralegal_perm_issues=[],
        paralegal_perm_missing_issues=[],
    )
    response = superuser_client.post(url)
    assert response.status_code == 200
    mock_reset_ms_access.assert_called_with(user)
    resp_data = response.json()
    assert resp_data["account"]["id"] == user.pk
    assert resp_data["permissions"] == {
        "has_coordinator_perms": False,
        "paralegal_perm_issues": [],
        "paralegal_perm_missing_issues": [],
    }
    assert list(user.groups.all()) == [paralegal_group]


@pytest.mark.django_db
@patch("case.views.accounts.reset_ms_access")
@patch("case.views.accounts.get_user_permissions")
def test_demote_account_permissions_view__as_paralegal(
    mock_get_user_permissions,
    mock_reset_ms_access,
    superuser_client: APIClient,
    paralegal_group,
):
    user = UserFactory()
    user.groups.set([paralegal_group])
    url = reverse("account-api-perms-demote", args=(user.pk,))
    mock_get_user_permissions.return_value = MicrosoftUserPermissions(
        has_coordinator_perms=False,
        paralegal_perm_issues=[],
        paralegal_perm_missing_issues=[],
    )
    response = superuser_client.post(url)
    assert response.status_code == 200
    mock_reset_ms_access.assert_not_called()
    resp_data = response.json()
    assert resp_data["account"]["id"] == user.pk
    assert resp_data["permissions"] == {
        "has_coordinator_perms": False,
        "paralegal_perm_issues": [],
        "paralegal_perm_missing_issues": [],
    }
    assert set(user.groups.all()) == set()


@pytest.mark.django_db
@patch("case.views.accounts.reset_ms_access")
@patch("case.views.accounts.get_user_permissions")
def test_demote_account_permissions_view__as_coordinator(
    mock_get_user_permissions,
    mock_reset_ms_access,
    superuser_client: APIClient,
    paralegal_group,
    coordinator_group,
):
    user = UserFactory()
    user.groups.set([coordinator_group, paralegal_group])
    url = reverse("account-api-perms-demote", args=(user.pk,))
    mock_get_user_permissions.return_value = MicrosoftUserPermissions(
        has_coordinator_perms=False,
        paralegal_perm_issues=[],
        paralegal_perm_missing_issues=[],
    )
    response = superuser_client.post(url)
    assert response.status_code == 200
    mock_reset_ms_access.assert_not_called()
    resp_data = response.json()
    assert resp_data["account"]["id"] == user.pk
    assert resp_data["permissions"] == {
        "has_coordinator_perms": False,
        "paralegal_perm_issues": [],
        "paralegal_perm_missing_issues": [],
    }
    assert set(user.groups.all()) == {paralegal_group}
