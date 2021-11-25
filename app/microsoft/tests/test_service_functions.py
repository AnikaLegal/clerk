from unittest import mock
import pytest

from microsoft.service import set_up_new_user
from microsoft.endpoints import MSGraphAPI

from core.factories import UserFactory


@pytest.fixture
def mock_client():
    """DRY: stub helper methods called by the service function for each test case."""
    with mock.patch("microsoft.endpoints.create_client") as mock_create_client:
        mock_client = mock.Mock()
        mock_client.acquire_token_silent.return_value = {"access_token": "1812"}
        mock_create_client.return_value = mock_client
        yield mock_client


def test_MSGraphAPI(mock_client):
    """Check MSGraphAPI constructor obtains access token and uses it to instantiate Endpoint objects."""
    api = MSGraphAPI()

    mock_client.acquire_token_silent.assert_called_once()
    assert api.group.headers["Authorization"] == "Bearer 1812"
    assert api.user.headers["Authorization"] == "Bearer 1812"
    assert api.folder.headers["Authorization"] == "Bearer 1812"
