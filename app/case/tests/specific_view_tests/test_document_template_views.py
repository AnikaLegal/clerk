from unittest.mock import MagicMock, patch


import pytest
from conftest import schema_tester
from core.factories import DocumentTemplateFactory
from core.models.document_template import DocumentTemplate
from core.models.issue import CaseTopic
from django.core.files.uploadedfile import SimpleUploadedFile
from django.utils import timezone
from microsoft.storage import MSGraphStorage
from rest_framework.reverse import reverse
from rest_framework.test import APIClient


@pytest.mark.django_db
def test_document_template_list_api_view(superuser_client: APIClient):
    template = DocumentTemplateFactory(
        topic=CaseTopic.REPAIRS,
        file=SimpleUploadedFile(
            name="template_1.txt",
            content=b"",
            content_type="text/plain",
        ),
    )
    DocumentTemplateFactory(
        topic=CaseTopic.BONDS,
        file=SimpleUploadedFile(
            name="template_2.txt",
            content=b"",
            content_type="text/plain",
        ),
    )

    url = "http://example.com/file"
    now = timezone.now()
    with (
        patch.object(MSGraphStorage, "url", return_value=url),
        patch.object(MSGraphStorage, "get_created_time", return_value=now),
        patch.object(MSGraphStorage, "get_modified_time", return_value=now),
    ):
        response = superuser_client.get(
            reverse("template-doc-api-list"), data={"topic": "REPAIRS"}
        )

    assert response.status_code == 200, response.json()

    json = response.json()
    assert len(json) == 1
    assert json[0]["id"] == template.id
    assert json[0]["name"] == template.name
    assert json[0]["url"] == url
    assert json[0]["created_at"] == timezone.localtime(now).strftime("%d/%m/%Y")
    assert json[0]["modified_at"] == timezone.localtime(now).strftime("%d/%m/%Y")
    assert json[0]["topic"] == template.topic

    schema_tester.validate_response(response=response)


@pytest.mark.django_db
def test_document_template_create_api_view(superuser_client: APIClient):
    file_a = SimpleUploadedFile(
        name="file_a.txt",
        content=b"file a content",
        content_type="text/plain",
    )
    file_b = SimpleUploadedFile(
        name="file_b.txt",
        content=b"file b content",
        content_type="text/plain",
    )

    assert DocumentTemplate.objects.count() == 0

    with patch.object(MSGraphStorage, "exists", return_value=False):

        def _save_return_value(name, content):
            return name

        with patch.object(MSGraphStorage, "_save", new_callable=MagicMock) as mock_save:
            mock_save.side_effect = _save_return_value

            data = {"topic": "REPAIRS", "files": [file_a, file_b]}
            response = superuser_client.post(
                reverse("template-doc-api-list"), data=data
            )

    assert response.status_code == 201, response.json()
    schema_tester.validate_response(response=response)

    assert (
        DocumentTemplate.objects.filter(topic="REPAIRS", file__isnull=False).count()
        == 2
    )


@pytest.mark.django_db
def test_document_template_destroy_api_view(superuser_client: APIClient):
    template = DocumentTemplateFactory(
        topic=CaseTopic.BONDS,
        file=SimpleUploadedFile(
            name="template.txt",
            content=b"",
            content_type="text/plain",
        ),
    )
    assert DocumentTemplate.objects.count() == 1

    response = superuser_client.delete(
        reverse("template-doc-api-detail", args=(template.pk,))
    )
    assert response.status_code == 204, response.json()
    schema_tester.validate_response(response=response)

    assert DocumentTemplate.objects.count() == 0
