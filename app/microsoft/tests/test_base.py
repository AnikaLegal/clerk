from unittest.mock import MagicMock, patch

import pytest
import requests
from microsoft.endpoints.base import BaseEndpoint, MSGraphTokenError


@pytest.fixture
def mock_client():
    return MagicMock()


@pytest.fixture
def endpoint(mock_client):
    return BaseEndpoint(mock_client)


@pytest.fixture
def endpoint_with_headers(mock_client):
    with patch(
        "microsoft.endpoints.base.BaseEndpoint.headers", new_callable=MagicMock
    ) as mock_headers:
        mock_headers.return_value = {"Authorization": "Bearer abc123"}
        yield BaseEndpoint(mock_client)


@patch("microsoft.endpoints.base.get_token")
def test_token_property_returns_token(mock_get_token, endpoint):
    mock_get_token.return_value = "abc123"
    assert endpoint.token == "abc123"


@patch("microsoft.endpoints.base.get_token")
def test_token_property_returns_none(mock_get_token, endpoint):
    mock_get_token.return_value = None
    assert endpoint.token is None


@patch("microsoft.endpoints.base.get_token")
def test_headers_returns_headers_with_auth(mock_get_token, endpoint):
    mock_get_token.return_value = "abc123"
    headers = endpoint.headers
    assert headers["Authorization"] == "Bearer abc123"


@patch("microsoft.endpoints.base.get_token")
def test_headers_raises_when_no_token(mock_get_token, endpoint):
    mock_get_token.return_value = None
    with pytest.raises(MSGraphTokenError):
        _ = endpoint.headers


@patch("microsoft.endpoints.base.requests.get")
def test_get_calls_requests_get(mock_requests_get, endpoint_with_headers):
    mock_resp = MagicMock()
    mock_resp.content = b'{"foo": "bar"}'
    mock_resp.json.return_value = {"foo": "bar"}
    mock_resp.raise_for_status.return_value = None
    mock_requests_get.return_value = mock_resp

    with patch.object(
        endpoint_with_headers, "handle", return_value={"foo": "bar"}
    ) as mock_handle:
        result = endpoint_with_headers.get("/test")
        mock_requests_get.assert_called_once()
        mock_handle.assert_called_once_with(mock_resp)
        assert result == {"foo": "bar"}


@patch("microsoft.endpoints.base.requests.get")
def test_get_list_pagination(mock_requests_get, endpoint_with_headers):
    # First response with nextLink
    resp1 = MagicMock()
    resp1.content = b'{"value": [1,2], "@odata.nextLink": "next"}'
    resp1.json.return_value = {"value": [1, 2], "@odata.nextLink": "next"}
    resp1.raise_for_status.return_value = None

    # Second response without nextLink
    resp2 = MagicMock()
    resp2.content = b'{"value": [3,4]}'
    resp2.json.return_value = {"value": [3, 4]}
    resp2.raise_for_status.return_value = None

    mock_requests_get.side_effect = [resp1, resp2]

    with patch.object(
        endpoint_with_headers,
        "handle",
        side_effect=[resp1.json.return_value, resp2.json.return_value],
    ):
        result = endpoint_with_headers.get_list("/test")
        assert result == [1, 2, 3, 4]
        assert mock_requests_get.call_count == 2


@patch("microsoft.endpoints.base.requests.post")
def test_post_calls_requests_post(mock_requests_post, endpoint_with_headers):
    mock_resp = MagicMock()
    mock_resp.content = b'{"foo": "bar"}'
    mock_resp.json.return_value = {"foo": "bar"}
    mock_resp.raise_for_status.return_value = None
    mock_requests_post.return_value = mock_resp

    with patch.object(
        endpoint_with_headers, "handle", return_value={"foo": "bar"}
    ) as mock_handle:
        result = endpoint_with_headers.post("/test", {"data": 1})
        mock_requests_post.assert_called_once()
        mock_handle.assert_called_once_with(mock_resp)
        assert result == {"foo": "bar"}


@patch("microsoft.endpoints.base.requests.patch")
def test_patch_calls_requests_patch(mock_requests_patch, endpoint_with_headers):
    mock_resp = MagicMock()
    mock_resp.content = b'{"foo": "bar"}'
    mock_resp.json.return_value = {"foo": "bar"}
    mock_resp.raise_for_status.return_value = None
    mock_requests_patch.return_value = mock_resp

    with patch.object(
        endpoint_with_headers, "handle", return_value={"foo": "bar"}
    ) as mock_handle:
        result = endpoint_with_headers.patch("/test", {"data": 1})
        mock_requests_patch.assert_called_once()
        mock_handle.assert_called_once_with(mock_resp)
        assert result == {"foo": "bar"}


@patch("microsoft.endpoints.base.requests.delete")
def test_delete_calls_requests_delete(mock_requests_delete, endpoint_with_headers):
    mock_resp = MagicMock()
    mock_resp.content = b'{"foo": "bar"}'
    mock_resp.json.return_value = {"foo": "bar"}
    mock_resp.raise_for_status.return_value = None
    mock_requests_delete.return_value = mock_resp

    with patch.object(
        endpoint_with_headers, "handle", return_value={"foo": "bar"}
    ) as mock_handle:
        result = endpoint_with_headers.delete("/test")
        mock_requests_delete.assert_called_once()
        mock_handle.assert_called_once_with(mock_resp)
        assert result == {"foo": "bar"}


def test_handle_successful_response(endpoint):
    resp = MagicMock()
    resp.content = b'{"foo": "bar"}'
    resp.json.return_value = {"foo": "bar"}
    resp.raise_for_status.return_value = None
    assert endpoint.handle(resp) == {"foo": "bar"}


def test_handle_404_response(endpoint):
    resp = MagicMock()
    resp.content = b"{}"
    resp.json.return_value = {}
    resp.raise_for_status.side_effect = requests.exceptions.HTTPError()
    resp.status_code = 404
    assert endpoint.handle(resp) is None


def test_handle_other_http_error_logs_and_raises(endpoint):
    resp = MagicMock()
    resp.content = b"{}"
    resp.json.return_value = {}
    resp.raise_for_status.side_effect = requests.exceptions.HTTPError()
    resp.status_code = 500
    resp.request.method = "GET"
    resp.request.url = "http://example.com"
    with pytest.raises(requests.exceptions.HTTPError):
        endpoint.handle(resp)
