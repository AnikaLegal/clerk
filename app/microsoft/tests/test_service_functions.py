from unittest import mock
import pytest

from microsoft.service import (
    TEMPLATE_PATHS,
    set_up_new_user,
    set_up_new_case,
    add_user_to_case,
    set_up_coordinator,
    tear_down_coordinator,
)
from microsoft.endpoints import MSGraphAPI
from core.factories import UserFactory, IssueFactory

from django.conf import settings


@pytest.fixture
def mock_client():
    """Stub helper methods called when MSGraphAPI object is created."""
    with mock.patch("microsoft.endpoints.create_client") as mock_create_client:
        mock_client = mock.Mock()
        mock_client.acquire_token_silent.return_value = {"access_token": "1812"}
        mock_create_client.return_value = mock_client
        yield mock_client


@pytest.fixture
def mock_api():
    """Mock MSGraphAPI object instantiated by each service function."""
    with mock.patch("microsoft.service.MSGraphAPI") as mock_MSGraphAPI:
        mock_api = mock.Mock()
        mock_MSGraphAPI.return_value = mock_api
        yield mock_api


def test_MSGraphAPI(mock_client):
    """MSGraphAPI constructor obtains access token and uses it to instantiate Endpoint objects."""
    api = MSGraphAPI()

    mock_client.acquire_token_silent.assert_called_once()
    assert api.group.headers["Authorization"] == "Bearer 1812"
    assert api.user.headers["Authorization"] == "Bearer 1812"
    assert api.folder.headers["Authorization"] == "Bearer 1812"


@pytest.mark.django_db
def test_set_up_new_user_A(mock_api):
    """Check service function does not create MS account or assign license for existing user."""
    user = UserFactory()
    mock_api.user.get.return_value = {
        f"Microsoft Account already exists for {user.email}"
    }

    set_up_new_user(user)

    mock_api.user.get.assert_called_once_with(user.email)
    mock_api.user.create.assert_not_called()
    mock_api.user.assign_license.assert_not_called()


@pytest.mark.django_db
def test_set_up_new_user_B(mock_api):
    """Check service function creates MS account and assigns license for new user."""
    user = UserFactory()
    mock_api.user.get.return_value = None
    mock_api.user.create.return_value = user, "open sesame"

    password = set_up_new_user(user)

    mock_api.user.get.assert_called_once_with(user.email)
    mock_api.user.create.assert_called_once_with(
        user.first_name, user.last_name, user.email
    )
    mock_api.user.assign_license.assert_called_once_with(user.email)
    assert password == "open sesame"


@pytest.mark.django_db
def test_set_up_new_case(mock_api):
    """Check service function creates new case folder and places it inside parent folder."""
    issue = IssueFactory()

    set_up_new_case(issue)

    mock_api.folder.copy.assert_called_once_with(
        TEMPLATE_PATHS[issue.topic], str(issue.id), settings.CASES_FOLDER_ID
    )


@pytest.mark.django_db
def test_add_user_to_case(mock_api):
    """Check service function gives user write permissions to existing case folder."""
    user = UserFactory()
    issue = IssueFactory()

    add_user_to_case(user, issue)

    mock_api.folder.create_permissions.assert_called_once_with(
        f"cases/{issue.id}", "write", [user.email]
    )


@pytest.mark.django_db
def test_set_up_coordinator_A(mock_api):
    """Check service function doesn't add User who is already a Group member."""
    user = UserFactory()
    mock_api.group.members.return_value = [user.email]

    set_up_coordinator(user)

    mock_api.group.members.assert_called_once()
    mock_api.group.add_user.assert_not_called()


@pytest.mark.django_db
def test_set_up_coordinator_B(mock_api):
    """Check service function adds User who is not already a Group member."""
    user = UserFactory()
    mock_api.group.members.return_value = []

    set_up_coordinator(user)

    mock_api.group.members.assert_called_once()
    mock_api.group.add_user.assert_called_once_with(user.email)


@pytest.mark.django_db
def test_tear_down_coordinator_A(mock_api):
    """Check service function removes User who is already a Group member."""
    user = UserFactory()
    mock_api.group.members.return_value = [user.email]
    mock_api.user.get.return_value = {"id": user.id}

    tear_down_coordinator(user)

    mock_api.group.members.assert_called_once()
    mock_api.user.get.assert_called_once_with(user.email)
    mock_api.group.remove_user.assert_called_once_with(user.id)


@pytest.mark.django_db
def test_tear_down_coordinator_B(mock_api):
    """Check service function doesn't remove User who is not already a Group member."""
    user = UserFactory()
    mock_api.group.members.return_value = []

    tear_down_coordinator(user)

    mock_api.group.members.assert_called_once()
    mock_api.user.get.assert_not_called()
    mock_api.group.remove_user.assert_not_called()
