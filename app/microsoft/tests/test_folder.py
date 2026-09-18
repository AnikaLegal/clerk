from unittest.mock import MagicMock, patch

import pytest
from microsoft.endpoints.folder import FILE_UPLOAD_SIZE_LIMIT, FolderEndpoint


@pytest.fixture
def endpoint():
    with patch(
        "microsoft.endpoints.base.BaseEndpoint.headers", new_callable=MagicMock
    ) as mock_headers:
        mock_headers.return_value = {"Authorization": "Bearer abc123"}
        yield FolderEndpoint(MagicMock())


@pytest.fixture
def mock_resp():
    resp = MagicMock()
    resp.content = b'{"id": "abc123", "uploadUrl": "https://example.com/upload"}'
    resp.json.return_value = {
        "id": "abc123",
        "uploadUrl": "https://example.com/upload",
    }
    resp.raise_for_status.return_value = None
    return resp


def test_small_file_upload_is_given_a_timeout(endpoint, mock_resp):
    """
    Without a timeout a hung MS Graph connection blocks the caller forever.
    """
    file = MagicMock(size=FILE_UPLOAD_SIZE_LIMIT - 1)

    with patch(
        "microsoft.endpoints.folder.requests.put", return_value=mock_resp
    ) as mock_put:
        endpoint.upload_file(file, "parent123", name="lease.pdf")

    assert mock_put.call_args.kwargs.get("timeout") is not None


def test_large_file_upload_is_given_a_timeout(endpoint, mock_resp):
    """
    Without a timeout a hung MS Graph connection blocks the caller forever.
    """
    file = MagicMock(size=FILE_UPLOAD_SIZE_LIMIT + 1)
    file.read.side_effect = [b"x" * (FILE_UPLOAD_SIZE_LIMIT + 1), b""]

    with (
        patch(
            "microsoft.endpoints.folder.requests.post", return_value=mock_resp
        ) as mock_post,
        patch(
            "microsoft.endpoints.folder.requests.put", return_value=mock_resp
        ) as mock_put,
        patch.object(endpoint, "get_child_if_exists", return_value={"id": "abc123"}),
    ):
        endpoint.upload_file(file, "parent123", name="lease.pdf")

    assert mock_post.call_args.kwargs.get("timeout") is not None
    assert mock_put.call_args.kwargs.get("timeout") is not None


def test_file_download_is_given_a_timeout(endpoint):
    """
    Without a timeout a hung MS Graph connection blocks the caller forever.
    """
    resp = MagicMock()
    resp.content = b'{"name": "lease.pdf", "file": {"mimeType": "application/pdf"}}'
    resp.json.return_value = {
        "name": "lease.pdf",
        "file": {"mimeType": "application/pdf"},
    }
    resp.raise_for_status.return_value = None

    with (
        patch("microsoft.endpoints.base.requests.get", return_value=resp),
        patch(
            "microsoft.endpoints.folder.requests.get", return_value=resp
        ) as mock_get,
    ):
        endpoint.download_file("abc123")

    assert mock_get.call_args.kwargs.get("timeout") is not None
