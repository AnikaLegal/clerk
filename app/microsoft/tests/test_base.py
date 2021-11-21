import pytest
import responses
import requests
from unittest import mock

from microsoft.endpoints.base import BaseEndpoint
from microsoft.endpoints.helpers import BASE_URL

TEST_URL = "https://github.com/getsentry/responses"


def test_constructor():
    base = BaseEndpoint("1812")

    assert base.headers["Authorization"] == "Bearer 1812"


@responses.activate
def test_handle_success_body():
    responses.add(
        responses.GET,
        TEST_URL,
        json={"message": "test request success"},
        status=200,
    )

    base = BaseEndpoint("1812")
    resp = requests.get(TEST_URL)
    result = base.handle(resp)

    assert result["message"] == "test request success"


@responses.activate
def test_handle_success_nobody():
    responses.add(
        responses.GET,
        TEST_URL,
        status=200,
    )

    base = BaseEndpoint("1812")
    resp = requests.get(TEST_URL)
    result = base.handle(resp)

    assert result == None


@responses.activate
def test_handle_fail_body():
    responses.add(
        responses.GET,
        TEST_URL,
        json={"message": "test request fail"},
        status=500,
    )

    with pytest.raises(requests.HTTPError):
        base = BaseEndpoint("1812")
        resp = requests.get(TEST_URL)
        base.handle(resp)


@responses.activate
def test_handle_fail_nobody():
    responses.add(
        responses.GET,
        TEST_URL,
        status=500,
    )

    with pytest.raises(requests.HTTPError):
        base = BaseEndpoint("1812")
        resp = requests.get(TEST_URL)
        base.handle(resp)


@responses.activate
def test_get_success():
    userPrincipalName = "bugs.bunny@anikalegal.com"
    responses.add(
        responses.GET,
        BASE_URL + "users/" + userPrincipalName,
        json={"userPrincipalName": userPrincipalName},
        status=200,
    )

    base = BaseEndpoint("1812")
    result = base.get("users/" + userPrincipalName)

    assert result["userPrincipalName"] == userPrincipalName


@responses.activate
def test_get_fail():
    userPrincipalName = "buy.bunny@anikalegal.com"
    responses.add(
        responses.GET,
        BASE_URL + "users/" + userPrincipalName,
        json={"error": {"code": "Request_ResourceNotFound"}},
        status=404,
    )

    base = BaseEndpoint("1812")
    result = base.get("users/" + userPrincipalName)

    assert result == None
