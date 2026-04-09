from unittest.mock import patch

import pytest
from accounts.models import User
from core.factories import UserFactory
from microsoft.service import MicrosoftUserPermissions
from rest_framework.reverse import reverse
from rest_framework.test import APIClient
from conftest import schema_tester


@pytest.mark.django_db
@patch("microsoft.tasks._invite_user_if_not_exists")
def test_account_api_create(
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

    schema_tester.validate_response(response=response)


@pytest.mark.django_db
def test_account_api_create__with_external_email(
    superuser_client: APIClient,
):
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
def test_account_api_list(superuser_client: APIClient):
    superuser = User.objects.get(is_superuser=True)

    charlie = UserFactory(first_name="Charlie", last_name="Brown")
    sally = UserFactory(first_name="Sally", last_name="Brown")
    lucy = UserFactory(first_name="Lucy", last_name="Van Pelt")
    url = reverse("account-api-list")

    response = superuser_client.get(url)
    assert response.status_code == 200, response.json()
    data = response.json()
    assert len(data["results"]) == 4
    emails = {result["email"] for result in data["results"]}
    assert emails == {charlie.email, sally.email, lucy.email, superuser.email}

    schema_tester.validate_response(response=response)


@pytest.mark.django_db
def test_account_api_list__name_filter(superuser_client: APIClient):
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
def test_account_api_list__group_filter(
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
def test_account_api_list__is_active_filter(superuser_client: APIClient):
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
def test_account_api_update(
    superuser_client: APIClient,
):
    user = UserFactory(first_name="Lucy", last_name="Van Pelt")
    url = reverse("account-api-detail", args=(user.pk,))
    data = {
        "first_name": "Charlie",
        "last_name": "Brown",
    }
    response = superuser_client.patch(url, data, format="json")
    assert response.status_code == 200, response.json()
    user.refresh_from_db()
    assert user.first_name == "Charlie"
    assert user.last_name == "Brown"

    schema_tester.validate_response(response=response)


@pytest.mark.django_db
@patch("case.views.accounts.get_user_permissions")
def test_account_api_perms(mock_get_user_permissions, superuser_client: APIClient):
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

    schema_tester.validate_response(response=response)


@pytest.mark.django_db
@patch("case.views.accounts.reset_ms_access")
@patch("case.views.accounts.get_user_permissions")
def test_account_api_perms_resync(
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

    schema_tester.validate_response(response=response)


@pytest.mark.django_db
@patch("case.views.accounts.list_directory_users")
def test_account_api_list_potential_users__returns_active_users(
    mock_list_directory_users, superuser_client: APIClient
):
    """Test that potential users endpoint returns active users from Google Directory."""
    mock_list_directory_users.return_value = [
        {
            "primaryEmail": "charlie.brown@example.com",
            "name": {"givenName": "Charlie", "familyName": "Brown"},
            "suspended": False,
        },
        {
            "primaryEmail": "sally.brown@example.com",
            "name": {"givenName": "Sally", "familyName": "Brown"},
            "suspended": False,
        },
    ]

    url = reverse("account-api-potential")
    response = superuser_client.get(url)

    assert response.status_code == 200, response.json()
    data = response.json()
    assert len(data) == 2
    emails = {user["email"] for user in data}
    assert emails == {"charlie.brown@example.com", "sally.brown@example.com"}

    schema_tester.validate_response(response=response)


@pytest.mark.django_db
@patch("case.views.accounts.list_directory_users")
def test_account_api_list_potential_users__excludes_suspended_users(
    mock_list_directory_users, superuser_client: APIClient
):
    """Test that suspended users are excluded from potential users list."""
    mock_list_directory_users.return_value = [
        {
            "primaryEmail": "charlie.brown@example.com",
            "name": {"givenName": "Charlie", "familyName": "Brown"},
            "suspended": False,
        },
        {
            "primaryEmail": "suspended.user@example.com",
            "name": {"givenName": "Suspended", "familyName": "User"},
            "suspended": True,
        },
    ]

    url = reverse("account-api-potential")
    response = superuser_client.get(url)

    assert response.status_code == 200, response.json()
    data = response.json()
    assert len(data) == 1
    assert data[0]["email"] == "charlie.brown@example.com"


@pytest.mark.django_db
@patch("case.views.accounts.list_directory_users")
def test_account_api_list_potential_users__excludes_existing_users(
    mock_list_directory_users, superuser_client: APIClient
):
    """Test that users already in the system are excluded from potential users."""
    UserFactory(email="charlie.brown@example.com")

    mock_list_directory_users.return_value = [
        {
            "primaryEmail": "charlie.brown@example.com",
            "name": {"givenName": "Charlie", "familyName": "Brown"},
            "suspended": False,
        },
        {
            "primaryEmail": "sally.brown@example.com",
            "name": {"givenName": "Sally", "familyName": "Brown"},
            "suspended": False,
        },
    ]

    url = reverse("account-api-potential")
    response = superuser_client.get(url)

    assert response.status_code == 200, response.json()
    data = response.json()
    assert len(data) == 1
    assert data[0]["email"] == "sally.brown@example.com"


@pytest.mark.django_db
@pytest.mark.parametrize(
    "user_client_name, expected_status",
    [
        ("user_client", 403),
        ("paralegal_user_client", 403),
        ("lawyer_user_client", 403),
        ("coordinator_user_client", 403),
        ("admin_user_client", 201),
    ],
)
@patch("microsoft.tasks._invite_user_if_not_exists")
def test_account_api_create_permissions(
    mock_invite_user_if_not_exists,
    user_client_name: str,
    expected_status: int,
    request,
):
    """
    Test create account API perms for different users.
    """
    client = request.getfixturevalue(user_client_name)
    url = reverse("account-api-list")
    data = {
        "first_name": "Charlie",
        "last_name": "Brown",
        "email": "charlie.brown@anikalegal.com",
        "groups": ["Paralegal"],
    }
    response = client.post(url, data, format="json")
    assert response.status_code == expected_status, response.json()


@pytest.mark.django_db
@pytest.mark.parametrize(
    "user_client_name, expected_status",
    [
        ("user_client", 403),
        ("paralegal_user_client", 403),
        ("lawyer_user_client", 403),
        ("coordinator_user_client", 200),
        ("admin_user_client", 200),
    ],
)
def test_account_api_update_permissions(
    user_client_name: str,
    expected_status: int,
    request,
):
    """
    Test update account API perms for different users.
    """
    user = UserFactory()
    url = reverse("account-api-detail", args=(user.pk,))
    data = {
        "first_name": "Charlie",
        "last_name": "Brown",
    }
    client = request.getfixturevalue(user_client_name)
    response = client.put(url, data, format="json")
    assert response.status_code == expected_status, response.json()


@pytest.mark.django_db
@pytest.mark.parametrize(
    "user_client_name, expected_status",
    [
        ("user_client", 403),
        ("paralegal_user_client", 403),
        ("lawyer_user_client", 403),
        ("coordinator_user_client", 403),
        ("admin_user_client", 200),
    ],
)
def test_account_api_update_permissions__groups(
    user_client_name: str,
    expected_status: int,
    request,
):
    """
    Test update account API perms for different users.
    """
    user = UserFactory()
    assert user.groups.count() == 0
    url = reverse("account-api-detail", args=(user.pk,))
    data = {
        "groups": ["Admin"],
    }
    client = request.getfixturevalue(user_client_name)
    response = client.put(url, data, format="json")
    assert response.status_code == expected_status, response.json()


@pytest.mark.django_db
@pytest.mark.parametrize(
    "user_client_name, expected_status",
    [
        ("user_client", 403),
        ("paralegal_user_client", 403),
        ("lawyer_user_client", 403),
        ("coordinator_user_client", 403),
        ("admin_user_client", 200),
    ],
)
@patch("case.views.accounts.list_directory_users")
def test_account_api_list_potential_users_permissions(
    mock_list_directory_users,
    user_client_name: str,
    expected_status: int,
    request,
):
    """
    Test list API perms for different users.
    """
    client = request.getfixturevalue(user_client_name)
    url = reverse("account-api-potential")
    response = client.get(url)

    assert response.status_code == expected_status
