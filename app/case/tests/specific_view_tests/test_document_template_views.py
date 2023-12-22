from io import BytesIO
from unittest.mock import patch

import pytest
from rest_framework.reverse import reverse
from rest_framework.test import APIClient
from django.core.files.uploadedfile import InMemoryUploadedFile

from conftest import schema_tester


@pytest.mark.django_db
@patch("case.views.document_templates.list_templates")
def test_document_template_list_api_view(
    mock_list_templates, superuser_client: APIClient
):
    mock_list_templates.return_value = [
        {
            "id": "1",
            "name": "foo",
            "url": "3",
            "created_at": "4",
            "modified_at": "5",
        },
        {
            "id": "1",
            "name": "bar",
            "url": "3",
            "created_at": "4",
            "modified_at": "5",
        },
    ]

    list_view_name = "template-doc-api-list"
    url = reverse(list_view_name)
    params = {"name": "foo", "topic": "baz"}
    response = superuser_client.get(url, data=params)

    # Check results
    mock_list_templates.assert_called_once_with("baz")
    schema_tester.validate_response(response=response)
    assert response.status_code == 200, response.json()
    assert response.json() == [
        {
            "id": "1",
            "name": "foo",
            "url": "3",
            "created_at": "4",
            "modified_at": "5",
            "topic": "baz",
        }
    ]


@pytest.mark.django_db
@patch("case.views.document_templates.upload_template")
def test_document_template_create_api_view(
    mock_upload_template, superuser_client: APIClient
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
    list_view_name = "template-doc-api-list"
    url = reverse(list_view_name)
    data = {"topic": "REPAIRS", "files": [file_a, file_b]}
    response = superuser_client.post(url, data=data)
    assert response.status_code == 201, response.json()
    assert mock_upload_template._mock_call_count == 2
    call_1, call_2 = mock_upload_template._mock_call_args_list
    assert call_1[0][0] == "REPAIRS"
    assert call_2[0][0] == "REPAIRS"
    assert call_1[0][1].name == "file_a.txt"
    assert call_2[0][1].name == "file_b.txt"
    schema_tester.validate_response(response=response)


@pytest.mark.django_db
@patch("case.views.document_templates.delete_template")
def test_document_template_destroy_api_view(
    mock_delete_template, superuser_client: APIClient
):
    file_id = "some-file-id"
    detail_view_name = "template-doc-api-detail"
    url = reverse(detail_view_name, args=(file_id,))
    response = superuser_client.delete(url)
    assert response.status_code == 204, response.json()
    mock_delete_template.assert_called_once_with(file_id=file_id)
    schema_tester.validate_response(response=response)
