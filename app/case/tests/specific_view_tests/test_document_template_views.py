from io import BytesIO
from unittest.mock import ANY, patch

import pytest
from conftest import schema_tester
from django.core.files.uploadedfile import InMemoryUploadedFile
from rest_framework.reverse import reverse
from rest_framework.test import APIClient


@pytest.mark.django_db
@patch("case.views.document_templates.list_path")
def test_document_template_list_api_view(mock_list_path, superuser_client: APIClient):
    mock_list_path.return_value = [
        {
            "id": "1",
            "name": "foo",
            "webUrl": "3",
            "createdDateTime": "2025-05-12T02:42:24+00:00",
            "lastModifiedDateTime": "2025-05-12T02:42:24+00:00",
        },
        {
            "id": "1",
            "name": "bar",
            "webUrl": "3",
            "createdDateTime": "2025-05-12T02:42:24+00:00",
            "lastModifiedDateTime": "2025-05-12T02:42:24+00:00",
        },
    ]

    url = reverse("template-doc-api-list")
    params = {"name": "foo", "topic": "REPAIRS"}
    response = superuser_client.get(url, data=params)

    # Check results
    mock_list_path.assert_called_once_with("templates/repairs")
    schema_tester.validate_response(response=response)
    assert response.status_code == 200, response.json()
    assert response.json() == [
        {
            "id": "1",
            "name": "foo",
            "url": "3",
            "created_at": "12/05/2025",
            "modified_at": "12/05/2025",
            "topic": "REPAIRS",
        }
    ]


@pytest.mark.django_db
@patch("case.serializers.documents.upload_file")
def test_document_template_create_api_view(
    mock_upload_file, superuser_client: APIClient
):
    file_a = InMemoryUploadedFile(
        BytesIO(b"file a content"),
        field_name="files",
        content_type="text/plain",
        size=14,
        charset=None,
        name="file_a.txt",
    )
    file_b = InMemoryUploadedFile(
        BytesIO(b"file b content"),
        field_name="files",
        content_type="text/plain",
        size=14,
        charset=None,
        name="file_b.txt",
    )

    url = reverse("template-doc-api-list")
    data = {"topic": "REPAIRS", "files": [file_a, file_b]}
    response = superuser_client.post(url, data=data)

    assert response.status_code == 201, response.json()
    assert mock_upload_file._mock_call_count == 2

    call_1, call_2 = mock_upload_file._mock_call_args_list
    assert call_1[0][0] == "templates/repairs"
    assert call_1[0][1].name == "file_a.txt"
    assert call_2[0][0] == "templates/repairs"
    assert call_2[0][1].name == "file_b.txt"

    schema_tester.validate_response(response=response)


@pytest.mark.django_db
@patch("case.views.document_templates.delete_file")
def test_document_template_destroy_api_view(
    mock_delete_file, superuser_client: APIClient
):
    file_id = "some-file-id"
    url = reverse(
        "template-doc-api-detail",
        args=(file_id,),
    )
    response = superuser_client.delete(url)
    assert response.status_code == 204, response.json()
    mock_delete_file.assert_called_once_with(file_id=file_id, allowed_path=ANY)
    schema_tester.validate_response(response=response)
