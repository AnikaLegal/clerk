from unittest.mock import patch

import pytest
from rest_framework.test import APIClient
from rest_framework.reverse import reverse

from accounts.models import User
from case.middleware import annotate_group_access
from core import factories
from core.models import IssueNote
from conftest import schema_tester


@pytest.mark.django_db
def test_case_list_view__with_no_access(user_client: APIClient, user: User):
    """
    Logged in, but otherwise unauthorized, users can fetch cases but no results
    """
    factories.IssueFactory()  # There's an issue but the user can't see it
    annotate_group_access(user)
    url = reverse("case-api-list")
    response = user_client.get(url)
    assert response.status_code == 200
    assert response.json() == {
        "current": 1,
        "item_count": 0,
        "next": None,
        "page_count": 1,
        "prev": None,
        "results": [],
    }
    schema_tester.validate_response(response=response)


@pytest.mark.django_db
def test_case_list_view__as_paralegal_with_no_access(
    user_client: APIClient,
    user: User,
    paralegal_group,
):
    """
    Paralegal users can fetch cases but no results because they're not assigned
    """
    factories.IssueFactory()  # There's an issue but the user can't see it
    user.groups.set([paralegal_group])
    annotate_group_access(user)
    url = reverse("case-api-list")
    response = user_client.get(url)
    assert response.status_code == 200
    assert response.json() == {
        "current": 1,
        "item_count": 0,
        "next": None,
        "page_count": 1,
        "prev": None,
        "results": [],
    }
    schema_tester.validate_response(response=response)


@pytest.mark.django_db
def test_case_list_view__as_paralegal_with_access(
    user_client: APIClient,
    user: User,
    paralegal_group,
):
    """
    Paralegal users can fetch cases and see results when they're assigned
    """
    issue_a = factories.IssueFactory(paralegal=user)
    factories.IssueFactory()  # There's an issue but the user can't see it
    user.groups.set([paralegal_group])
    annotate_group_access(user)
    url = reverse("case-api-list")
    response = user_client.get(url)
    assert response.status_code == 200
    resp_data = response.json()

    resp_data["current"] == 1
    resp_data["item_count"] == 1
    resp_data["page_count"] == 1
    resp_data["next"] == None
    resp_data["prev"] == None
    results = resp_data["results"]
    assert len(results) == 1
    assert results[0]["id"] == str(issue_a.pk)
    schema_tester.validate_response(response=response)


@pytest.mark.django_db
def test_case_list_view__as_coordinator(
    user_client: APIClient,
    user: User,
    coordinator_group,
):
    """
    Coordinator users can fetch cases and see results
    """
    issue_a = factories.IssueFactory(paralegal=user)
    issue_b = factories.IssueFactory()
    user.groups.set([coordinator_group])
    annotate_group_access(user)
    url = reverse("case-api-list")
    response = user_client.get(url)
    assert response.status_code == 200
    resp_data = response.json()

    resp_data["current"] == 1
    resp_data["item_count"] == 2
    resp_data["page_count"] == 1
    resp_data["next"] == None
    resp_data["prev"] == None
    results = resp_data["results"]
    assert len(results) == 2
    assert set(r["id"] for r in results) == {str(issue_a.pk), str(issue_b.pk)}
    schema_tester.validate_response(response=response)


@pytest.mark.django_db
def test_case_list_view__search(superuser_client: APIClient):
    issue_a = factories.IssueFactory(fileref="A12345")
    factories.IssueFactory(fileref="B54321")
    url = reverse("case-api-list")

    # No search results
    response = superuser_client.get(url, {"search": "qwsqwsqwsqws"})
    assert response.status_code == 200
    resp_data = response.json()
    resp_data["item_count"] == 0
    results = resp_data["results"]
    assert len(results) == 0

    # One search result
    response = superuser_client.get(url, {"search": "A12345"})
    assert response.status_code == 200
    resp_data = response.json()
    resp_data["item_count"] == 1
    results = resp_data["results"]
    assert len(results) == 1
    assert results[0]["id"] == str(issue_a.pk)
    schema_tester.validate_response(response=response)


# TODO: Test permissions and who can see which notes
@pytest.mark.django_db
def test_case_get_view(superuser_client: APIClient):
    issue = factories.IssueFactory()
    factories.IssueNoteFactory(issue=issue)
    factories.TenancyFactory(client=issue.client)
    url = reverse("case-api-detail", args=(issue.pk,))
    response = superuser_client.get(url)
    assert response.status_code == 200
    schema_tester.validate_response(response=response)


# TODO: Test permissions
@pytest.mark.django_db
def test_case_update_view(superuser_client: APIClient):
    issue = factories.IssueFactory(is_open=True)
    url = reverse("case-api-detail", args=(issue.pk,))
    response = superuser_client.patch(url, data={"is_open": False}, format="json")
    assert response.status_code == 200
    schema_tester.validate_response(response=response)
    issue.refresh_from_db()
    assert not issue.is_open


# TODO: Test permissions
@pytest.mark.django_db
def test_case_create_note_view(superuser_client: APIClient, superuser: User):
    issue = factories.IssueFactory()
    url = reverse("case-api-note", args=(issue.pk,))
    assert IssueNote.objects.count() == 0
    data = {
        "note_type": "PARALEGAL",
        "text": "Lorem ipsum dolor",
    }
    response = superuser_client.post(url, data=data, format="json")
    assert response.status_code == 201, response.json()
    schema_tester.validate_response(response=response)

    note = IssueNote.objects.get()
    assert note.creator == superuser
    assert note.note_type == "PARALEGAL"
    assert note.text == "Lorem ipsum dolor"
    assert note.issue == issue


# TODO: Test permissions
@pytest.mark.django_db
@patch("case.views.case.get_case_folder_info")
def test_case_get_documents_view(
    mock_get_case_folder_info, superuser_client: APIClient
):
    issue = factories.IssueFactory()
    url = reverse("case-api-docs", args=(issue.pk,))
    sharepoint_url = "http://example.com"
    docs = [
        {
            "name": "Name",
            "url": "http://example.com/blah",
            "id": "12345",
            "size": 99,
            "is_file": True,
        }
    ]
    mock_get_case_folder_info.return_value = docs, sharepoint_url
    response = superuser_client.get(url)
    mock_get_case_folder_info.assert_called_once_with(issue)
    schema_tester.validate_response(response=response)
