import pytest
import responses
import requests
from unittest import mock

from microsoft.wrapper import MSGraph

from django.conf import settings


@pytest.fixture
def mock_client():
    """DRY: mock the client when MSGraph object is created"""
    with mock.patch("microsoft.wrapper.create_client") as mock_create_client:
        mock_client = mock.Mock()
        mock_result = {"access_token": "1805"}
        mock_client.acquire_token_silent.return_value = mock_result
        mock_create_client.return_value = mock_client
        yield mock_client


def test_constructor(mock_client):
    api = MSGraph()

    mock_client.acquire_token_silent.assert_called_once()
    assert api.headers["Authorization"] == "Bearer 1805"
