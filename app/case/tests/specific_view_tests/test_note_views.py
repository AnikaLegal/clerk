import pytest
from conftest import CaseRole, schema_tester
from core.factories import IssueFactory, IssueNoteFactory
from core.models.issue_note import IssueNote, NoteType
from rest_framework.reverse import reverse
from rest_framework.test import APIClient

coordinator_note_types_only = list(
    set(IssueNote.COORDINATOR_NOTE_TYPES) - set(IssueNote.PARALEGAL_NOTE_TYPES)
)


@pytest.mark.django_db
def test_issue_note_list_api(superuser_client: APIClient):
    instance_1 = IssueNoteFactory()
    instance_2 = IssueNoteFactory()

    url = reverse("note-api-list")
    response = superuser_client.get(url)

    assert response.status_code == 200, response.json()
    data = response.json()

    # Pagination meta
    assert data["current"] == 1
    assert data["item_count"] == 2
    assert data["page_count"] == 1
    assert data["next"] is None
    assert data["prev"] is None

    results = data["results"]
    assert len(results) == 2
    assert set(x["id"] for x in results) == {instance_1.pk, instance_2.pk}

    schema_tester.validate_response(response=response)


@pytest.mark.django_db
def test_issue_note_list_api__search_filter(superuser_client: APIClient):
    instance_1 = IssueNoteFactory()
    instance_2 = IssueNoteFactory()
    url = reverse("note-api-list")

    # Empty search parameter - ignored
    response = superuser_client.get(url, {"issue": ""})
    assert response.status_code == 200
    resp_data = response.json()
    assert resp_data["item_count"] == 2
    results = resp_data["results"]
    assert len(results) == 2
    assert set(x["id"] for x in results) == {instance_1.pk, instance_2.pk}

    # No search results.
    response = superuser_client.get(
        url, {"issue": "00000000-0000-4000-8000-000000000000"}
    )
    assert response.status_code == 200
    resp_data = response.json()
    assert resp_data["item_count"] == 0
    results = resp_data["results"]
    assert len(results) == 0

    # One search result by issue id.
    response = superuser_client.get(url, {"issue": str(instance_1.issue.pk)})
    assert response.status_code == 200
    resp_data = response.json()
    assert resp_data["item_count"] == 1
    results = resp_data["results"]
    assert len(results) == 1
    assert results[0]["id"] == instance_1.pk
    schema_tester.validate_response(response=response)


@pytest.mark.django_db
@pytest.mark.parametrize(
    "user_name, assigned_as, expected_status, expected_count",
    [
        ("unprivileged_user", CaseRole.NONE, 403, None),
        ("unprivileged_user", CaseRole.PARALEGAL, 403, None),
        ("unprivileged_user", CaseRole.LAWYER, 403, None),
        ("paralegal_user", CaseRole.NONE, 200, 0),
        ("paralegal_user", CaseRole.PARALEGAL, 200, 0),
        ("paralegal_user", CaseRole.LAWYER, 200, 0),
        ("lawyer_user", CaseRole.NONE, 200, 0),
        ("lawyer_user", CaseRole.PARALEGAL, 200, 0),
        ("lawyer_user", CaseRole.LAWYER, 200, 0),
        ("coordinator_user", CaseRole.NONE, 200, 1),
        ("coordinator_user", CaseRole.PARALEGAL, 200, 1),
        ("coordinator_user", CaseRole.LAWYER, 200, 1),
        ("admin_user", CaseRole.NONE, 200, 1),
        ("admin_user", CaseRole.PARALEGAL, 200, 1),
        ("admin_user", CaseRole.LAWYER, 200, 1),
    ],
)
@pytest.mark.parametrize("note_type", coordinator_note_types_only)
def test_issue_note_api_list_coordinator_note_types(
    note_type: NoteType,
    user_name: str,
    assigned_as: CaseRole,
    expected_status: int,
    expected_count: int,
    user_client,
    request,
):
    """
    Test API list perms for different users on coordinator note types, which
    should only be visible to coordinators and above.
    """
    user = request.getfixturevalue(user_name)
    issue = IssueFactory()
    if assigned_as == CaseRole.PARALEGAL:
        issue.paralegal = user
        issue.save()
    elif assigned_as == CaseRole.LAWYER:
        issue.lawyer = user
        issue.save()
    IssueNoteFactory(issue=issue, note_type=note_type)

    url = reverse("note-api-list")
    response = user_client.get(url)

    assert response.status_code == expected_status

    if expected_count is not None:
        data = response.json()
        assert data["item_count"] == expected_count
        results = data["results"]
        assert len(results) == expected_count


@pytest.mark.django_db
@pytest.mark.parametrize(
    "user_name, assigned_as, expected_status, expected_count",
    [
        ("unprivileged_user", CaseRole.NONE, 403, None),
        ("unprivileged_user", CaseRole.PARALEGAL, 403, None),
        ("unprivileged_user", CaseRole.LAWYER, 403, None),
        ("paralegal_user", CaseRole.NONE, 200, 0),
        ("paralegal_user", CaseRole.PARALEGAL, 200, 1),
        ("paralegal_user", CaseRole.LAWYER, 200, 0),
        ("lawyer_user", CaseRole.NONE, 200, 0),
        ("lawyer_user", CaseRole.PARALEGAL, 200, 1),
        ("lawyer_user", CaseRole.LAWYER, 200, 1),
        ("coordinator_user", CaseRole.NONE, 200, 1),
        ("coordinator_user", CaseRole.PARALEGAL, 200, 1),
        ("coordinator_user", CaseRole.LAWYER, 200, 1),
        ("admin_user", CaseRole.NONE, 200, 1),
        ("admin_user", CaseRole.PARALEGAL, 200, 1),
        ("admin_user", CaseRole.LAWYER, 200, 1),
    ],
)
def test_issue_note_api_list_perms(
    user_name: str,
    assigned_as: CaseRole,
    expected_status: int,
    expected_count: int,
    user_client,
    request,
):
    """
    Test list API perms for different users.
    """
    user = request.getfixturevalue(user_name)
    issue = IssueFactory()
    if assigned_as == CaseRole.PARALEGAL:
        issue.paralegal = user
        issue.save()
    elif assigned_as == CaseRole.LAWYER:
        issue.lawyer = user
        issue.save()
    IssueNoteFactory(issue=issue, note_type=NoteType.PARALEGAL)

    url = reverse("note-api-list")
    response = user_client.get(url)

    assert response.status_code == expected_status

    if expected_count is not None:
        data = response.json()
        assert data["item_count"] == expected_count
        results = data["results"]
        assert len(results) == expected_count


@pytest.mark.django_db
@pytest.mark.parametrize(
    "user_name, assigned_as, expected_status, expected_count",
    [
        ("unprivileged_user", CaseRole.NONE, 403, None),
        ("unprivileged_user", CaseRole.PARALEGAL, 403, None),
        ("unprivileged_user", CaseRole.LAWYER, 403, None),
        ("paralegal_user", CaseRole.NONE, 200, 1),
        ("paralegal_user", CaseRole.PARALEGAL, 200, 1),
        ("paralegal_user", CaseRole.LAWYER, 200, 1),
        ("lawyer_user", CaseRole.NONE, 200, 1),
        ("lawyer_user", CaseRole.PARALEGAL, 200, 1),
        ("lawyer_user", CaseRole.LAWYER, 200, 1),
        ("coordinator_user", CaseRole.NONE, 200, 1),
        ("coordinator_user", CaseRole.PARALEGAL, 200, 1),
        ("coordinator_user", CaseRole.LAWYER, 200, 1),
        ("admin_user", CaseRole.NONE, 200, 1),
        ("admin_user", CaseRole.PARALEGAL, 200, 1),
        ("admin_user", CaseRole.LAWYER, 200, 1),
    ],
)
def test_issue_note_api_list_perms_as_creator(
    user_name: str,
    assigned_as: CaseRole,
    expected_status: int,
    expected_count: int,
    user_client,
    request,
):
    """
    Test API list perms for different users as the creator of the note.
    """
    user = request.getfixturevalue(user_name)
    issue = IssueFactory()
    if assigned_as == CaseRole.PARALEGAL:
        issue.paralegal = user
        issue.save()
    elif assigned_as == CaseRole.LAWYER:
        issue.lawyer = user
        issue.save()
    IssueNoteFactory(issue=issue, note_type=NoteType.PARALEGAL, creator=user)

    url = reverse("note-api-list")
    response = user_client.get(url)

    assert response.status_code == expected_status

    if expected_count is not None:
        data = response.json()
        assert data["item_count"] == expected_count
        results = data["results"]
        assert len(results) == expected_count
