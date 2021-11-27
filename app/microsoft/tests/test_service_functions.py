from unittest import mock
import pytest

from microsoft.service import set_up_new_user
from microsoft.endpoints import MSGraphAPI

from core.factories import UserFactory


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
    """Mock MSGraph API object instantiated by each service function."""
    with mock.patch("microsoft.service.MSGraphAPI") as mock_MSGraphAPI:
        mock_api = mock.Mock()
        mock_MSGraphAPI.return_value = mock_api
        yield mock_api


def test_MSGraphAPI(mock_client):
    """MSGraphAPI contructor obtains access token and uses it to instantiate Endpoint objects."""
    api = MSGraphAPI()

    mock_client.acquire_token_silent.assert_called_once()
    assert api.group.headers["Authorization"] == "Bearer 1812"
    assert api.user.headers["Authorization"] == "Bearer 1812"
    assert api.folder.headers["Authorization"] == "Bearer 1812"


@pytest.mark.django_db
def test_set_up_new_user_A(mock_api):
    """Check set_up_new_user service function works correctly for existing user."""
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
    """Check set_up_new_user service function works correctly for new user."""
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
