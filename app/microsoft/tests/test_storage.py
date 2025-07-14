import pytest
from unittest.mock import MagicMock, patch
from django.core.files.uploadedfile import SimpleUploadedFile
from microsoft.storage import MSGraphStorage


@pytest.fixture
def mock_api():
    api = MagicMock()
    api.folder.get.return_value = {
        "id": "file_id",
        "size": 123,
        "webUrl": "https://example.com",
    }
    api.folder.download_file.return_value = ("file.txt", "text/plain", b"content")
    api.folder.upload_file.return_value = {"id": "file_id", "name": "file.txt"}
    api.folder.create_path.return_value = None
    api.folder.delete_file.return_value = None
    return api


@pytest.fixture
def storage(mock_api):
    with patch("microsoft.storage.MSGraphAPI", return_value=mock_api):
        yield MSGraphStorage()


def test_get_file_info_cache(storage):
    storage.cache.set("file.txt", {"id": "cached"})
    info = storage._get_file_info("file.txt")
    assert info == {"id": "cached"}


def test_get_file_info_api(storage, mock_api):
    storage.cache.delete("file.txt")
    info = storage._get_file_info("file.txt")
    assert info["id"] == "file_id"
    mock_api.folder.get.assert_called_once()


def test_open_success(storage):
    file = storage._open("file.txt")
    assert isinstance(file, SimpleUploadedFile)
    assert file.read() == b"content"
    assert file.content_type == "text/plain"


def test_open_file_not_found(storage, mock_api):
    mock_api.folder.get.return_value = None
    with pytest.raises(FileNotFoundError):
        storage._open("missing.txt")


def test_save_existing_dir(storage):
    content = MagicMock()
    storage._get_file_info = MagicMock(return_value={"id": "dir_id"})
    storage.api.folder.upload_file = MagicMock(return_value={"name": "file.txt"})
    name = storage._save("dir/file.txt", content)
    storage.api.folder.upload_file.assert_called_once()
    assert name == "dir/file.txt"


def test_save_creates_dir(storage, mock_api):
    storage._get_file_info = MagicMock(side_effect=[None, {"id": "dir_id"}])
    storage.api.folder.create_path = MagicMock()
    content = MagicMock()
    name = storage._save("dir/file.txt", content)
    storage.api.folder.create_path.assert_called_once()
    assert name == "dir/file.txt"


def test_save_folder_not_found(storage, mock_api):
    storage._get_file_info = MagicMock(side_effect=[None, None])
    storage.api.folder.create_path = MagicMock()
    content = MagicMock()
    with pytest.raises(FileNotFoundError):
        storage._save("dir/file.txt", content)


def test_delete_file(storage, mock_api):
    storage._get_file_info = MagicMock(return_value={"id": "file_id"})
    storage.cache.delete = MagicMock()
    storage.delete("file.txt")
    mock_api.folder.delete_file.assert_called_once_with("file_id")
    storage.cache.delete.assert_called_once()


def test_delete_file_not_found(storage, mock_api):
    storage._get_file_info = MagicMock(return_value=None)
    storage.delete("file.txt")
    mock_api.folder.delete_file.assert_not_called()


def test_exists_true(storage):
    storage._get_file_info = MagicMock(return_value={"id": "file_id"})
    assert storage.exists("file.txt") is True


def test_exists_false(storage):
    storage._get_file_info = MagicMock(return_value=None)
    assert storage.exists("file.txt") is False


def test_get_valid_name(storage):
    assert storage.get_valid_name("file.txt") == "file.txt"


def test_size_success(storage):
    storage._get_file_info = MagicMock(return_value={"size": 42})
    assert storage.size("file.txt") == 42


def test_size_file_not_found(storage):
    storage._get_file_info = MagicMock(return_value=None)
    with pytest.raises(FileNotFoundError):
        storage.size("file.txt")


def test_url_success(storage):
    storage._get_file_info = MagicMock(return_value={"webUrl": "https://example.com"})
    assert storage.url("file.txt") == "https://example.com"


def test_url_file_not_found(storage):
    storage._get_file_info = MagicMock(return_value=None)
    assert storage.url("file.txt") == ""


def test_get_created_time_success(storage):
    storage._get_file_info = MagicMock(return_value={"createdDateTime": "2024-07-14T12:34:56+00:00"})
    dt = storage.get_created_time("file.txt")
    assert dt.isoformat() == "2024-07-14T12:34:56+00:00"


def test_get_created_time_file_not_found(storage):
    storage._get_file_info = MagicMock(return_value=None)
    with pytest.raises(FileNotFoundError):
        storage.get_created_time("file.txt")


def test_get_modified_time_success(storage):
    storage._get_file_info = MagicMock(return_value={"lastModifiedDateTime": "2024-07-14T12:34:56+00:00"})
    dt = storage.get_modified_time("file.txt")
    assert dt.isoformat() == "2024-07-14T12:34:56+00:00"


def test_get_modified_time_file_not_found(storage):
    storage._get_file_info = MagicMock(return_value=None)
    with pytest.raises(FileNotFoundError):
        storage.get_modified_time("file.txt")


def test_is_name_available_no_max_length(storage):
    assert storage.is_name_available("file.txt") is True


def test_is_name_available_exceeds_max_length(storage):
    assert storage.is_name_available("a" * 300, max_length=255) is False


def test_is_name_available_within_max_length(storage):
    assert storage.is_name_available("a" * 10, max_length=255) is True
