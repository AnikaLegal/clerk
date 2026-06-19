from unittest.mock import MagicMock, patch

import pytest
from core.factories import DocumentTemplateFactory
from core.models.document_template import DocumentTemplate
from core.models.issue import CaseTopic
from django.core.files.uploadedfile import SimpleUploadedFile
from django.utils import timezone
from microsoft.storage import MSGraphStorage
from rest_framework.reverse import reverse


@pytest.mark.django_db
def test_document_template_list_api_view(superuser_client):
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

    url = "https://example.com/file"
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


@pytest.mark.django_db
def test_document_template_create_api_view(superuser):
    # Manually test the response schema here due to bug in the openapi tester
    # where it doesn't use the correct content-type.
    # TODO: Remove when the openapi tester bug is fixed.
    from conftest import schema_tester
    from openapi_tester.response_handler_factory import ResponseHandlerFactory
    from rest_framework.test import APIClient

    superuser_client = APIClient()
    superuser_client.force_login(user=superuser)

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

    def _save_return_value(name, content):
        return name

    with (
        patch.object(MSGraphStorage, "exists", return_value=False),
        patch.object(MSGraphStorage, "_save", new_callable=MagicMock) as mock_save,
    ):
        mock_save.side_effect = _save_return_value

        data = {"topic": "REPAIRS", "files": [file_a, file_b]}
        response = superuser_client.post(
            reverse("template-doc-api-list"), data=data, format="multipart"
        )

    assert response.status_code == 201, response.json()

    assert (
        DocumentTemplate.objects.filter(topic="REPAIRS", file__isnull=False).count()
        == 2
    )

    schema_tester.validate_response(
        response_handler=ResponseHandlerFactory.create(response=response)
    )


@pytest.mark.django_db
def test_document_template_destroy_api_view(superuser_client):
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

    assert DocumentTemplate.objects.count() == 0


@pytest.mark.django_db
def test_document_template_rename_api_view(superuser_client):
    template = DocumentTemplateFactory(
        topic=CaseTopic.BONDS,
        file=SimpleUploadedFile(
            name="file.txt",
            content=b"",
            content_type="text/plain",
        ),
    )
    assert DocumentTemplate.objects.count() == 1

    new_name = "new_name.txt"

    def _save_return_value(name, content):
        return name

    with (
        patch.object(MSGraphStorage, "_open", return_value=template.file),
        patch.object(MSGraphStorage, "_save", new_callable=MagicMock) as mock_save,
        patch.object(MSGraphStorage, "exists", return_value=False),
    ):
        mock_save.side_effect = _save_return_value

        url = reverse("template-doc-api-rename-file", args=(template.pk,))
        response = superuser_client.patch(url, data={"name": new_name})

    assert response.status_code == 204, response.json()

    # The name property is an annotation so it won't be reset if we call
    # template.refresh_from_db() here as we might normally do, so we just get
    # the object instead.
    template = DocumentTemplate.objects.get(pk=template.pk)
    assert template.name == new_name
    assert template.file.name.endswith(new_name)


@pytest.mark.django_db
@pytest.mark.parametrize(
    "user_client_name, expected_status",
    [
        ("user_client", 403),
        ("paralegal_user_client", 403),
        ("coordinator_user_client", 403),
        ("admin_user_client", 200),
    ],
)
def test_document_template_api_list_perms(
    user_client_name: str,
    expected_status: int,
    request,
):
    """
    Test list API perms for different users.
    """
    client = request.getfixturevalue(user_client_name)
    with (
        patch.object(MSGraphStorage, "url", return_value="https://example.com/file"),
        patch.object(MSGraphStorage, "get_created_time", return_value=timezone.now()),
        patch.object(MSGraphStorage, "get_modified_time", return_value=timezone.now()),
    ):
        url = reverse("template-doc-api-list")
        response = client.get(url)

    assert response.status_code == expected_status


@pytest.mark.django_db
@pytest.mark.parametrize(
    "user_fixture_name, expected_status",
    [
        ("user", 403),
        ("paralegal_user", 403),
        ("coordinator_user", 403),
        ("admin_user", 201),
    ],
)
def test_document_template_api_create_perms(
    user_fixture_name: str,
    expected_status: int,
    request,
):
    """
    Test create API perms for different users.
    """
    # Manually test the response schema here due to bug in the openapi tester
    # where it doesn't use the correct content-type.
    # TODO: Remove when the openapi tester bug is fixed.
    from conftest import schema_tester
    from openapi_tester.response_handler_factory import ResponseHandlerFactory
    from rest_framework.test import APIClient

    user = request.getfixturevalue(user_fixture_name)
    client = APIClient()
    client.force_login(user=user)

    def _save_return_value(name, content):
        return name

    with (
        patch.object(MSGraphStorage, "exists", return_value=False),
        patch.object(MSGraphStorage, "_save", new_callable=MagicMock) as mock_save,
    ):
        mock_save.side_effect = _save_return_value

        url = reverse("template-doc-api-list")
        file = SimpleUploadedFile(
            name="file.txt",
            content=b"file content",
            content_type="text/plain",
        )
        data = {"topic": "REPAIRS", "files": [file]}
        response = client.post(url, data=data)

    assert response.status_code == expected_status

    schema_tester.validate_response(
        response_handler=ResponseHandlerFactory.create(response=response)
    )


@pytest.mark.django_db
@pytest.mark.parametrize(
    "user_client_name, expected_status",
    [
        ("user_client", 403),
        ("paralegal_user_client", 403),
        ("coordinator_user_client", 403),
        ("admin_user_client", 204),
    ],
)
def test_document_template_api_delete_perms(
    user_client_name: str,
    expected_status: int,
    request,
):
    """
    Test list API perms for different users.
    """
    client = request.getfixturevalue(user_client_name)

    template = DocumentTemplateFactory(
        topic=CaseTopic.BONDS,
        file=SimpleUploadedFile(
            name="file.txt",
            content=b"",
            content_type="text/plain",
        ),
    )
    url = reverse("template-doc-api-detail", args=(template.pk,))
    response = client.delete(url)

    assert response.status_code == expected_status


@pytest.mark.django_db
@pytest.mark.parametrize(
    "user_client_name, expected_status",
    [
        ("user_client", 403),
        ("paralegal_user_client", 403),
        ("coordinator_user_client", 403),
        ("admin_user_client", 204),
    ],
)
def test_document_template_api_rename_perms(
    user_client_name: str,
    expected_status: int,
    request,
):
    """
    Test list API perms for different users.
    """
    client = request.getfixturevalue(user_client_name)

    template = DocumentTemplateFactory(
        topic=CaseTopic.BONDS,
        file=SimpleUploadedFile(
            name="file.txt",
            content=b"",
            content_type="text/plain",
        ),
    )

    def _save_return_value(name, content):
        return name

    with (
        patch.object(MSGraphStorage, "_open", return_value=template.file),
        patch.object(MSGraphStorage, "_save", new_callable=MagicMock) as mock_save,
        patch.object(MSGraphStorage, "exists", return_value=False),
    ):
        mock_save.side_effect = _save_return_value

        url = reverse("template-doc-api-rename-file", args=(template.pk,))
        response = client.patch(url, data={"name": "new_name.txt"})

    assert response.status_code == expected_status
