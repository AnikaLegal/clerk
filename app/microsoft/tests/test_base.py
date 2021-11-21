import pytest
import responses
import requests

from microsoft.endpoints.base import BaseEndpoint
from microsoft.endpoints.helpers import BASE_URL

TEST_URL = "https://github.com/getsentry/responses"


@pytest.fixture
def base():
    """DRY: Initialise BaseEndpoint object with access token."""
    return BaseEndpoint("1812")


def test_constructor(base):
    """Constructor sets access token inside of header."""
    assert base.headers["Authorization"] == "Bearer 1812"


@responses.activate
def test_handle_success_body(base):
    """Handle method processes successful response with JSON."""
    responses.add(
        responses.GET,
        TEST_URL,
        json={"message": "test request success"},
        status=200,
    )

    resp = requests.get(TEST_URL)
    result = base.handle(resp)

    assert result["message"] == "test request success"


@responses.activate
def test_handle_success_nobody(base):
    """Handle method processes successful response without JSON."""
    responses.add(
        responses.GET,
        TEST_URL,
        status=200,
    )

    resp = requests.get(TEST_URL)
    result = base.handle(resp)

    assert result == None


@responses.activate
def test_handle_fail_body(base):
    """Handle method processes failed response (500) with JSON."""
    responses.add(
        responses.GET,
        TEST_URL,
        json={"message": "test request fail"},
        status=500,
    )

    with pytest.raises(requests.HTTPError):
        resp = requests.get(TEST_URL)
        base.handle(resp)


@responses.activate
def test_handle_fail_nobody(base):
    """Handle method processes failed response (500) without JSON."""
    responses.add(
        responses.GET,
        TEST_URL,
        status=500,
    )

    with pytest.raises(requests.HTTPError):
        resp = requests.get(TEST_URL)
        base.handle(resp)


@responses.activate
def test_get_success(base):
    """Get method makes successful request and processes the response."""
    userPrincipalName = "bugs.bunny@anikalegal.com"
    responses.add(
        responses.GET,
        BASE_URL + "users/" + userPrincipalName,
        json={"userPrincipalName": userPrincipalName},
        status=200,
    )

    result = base.get("users/" + userPrincipalName)

    assert result["userPrincipalName"] == userPrincipalName


@responses.activate
def test_get_fail(base):
    """Get method makes unsuccessful request (404) and processes the response."""
    userPrincipalName = "buy.bunny@anikalegal.com"
    responses.add(
        responses.GET,
        BASE_URL + "users/" + userPrincipalName,
        json={"error": {"code": "Request_ResourceNotFound"}},
        status=404,
    )

    result = base.get("users/" + userPrincipalName)

    assert result == None
