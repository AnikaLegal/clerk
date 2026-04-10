from enum import Enum
import pytest
from conftest import CaseRole, schema_tester
from core.factories import IssueFactory, SubmissionFactory
from rest_framework.reverse import reverse
from rest_framework.test import APIClient


class AssignedAs(Enum):
    NONE = 1
    PARALEGAL = 2
    LAWYER = 3


@pytest.mark.django_db
def test_submission_retrieve_api(superuser_client: APIClient):
    submission = SubmissionFactory(is_processed=True)
    url = reverse("submission-api-detail", args=(submission.pk,))
    response = superuser_client.get(url)

    assert response.status_code == 200, response.json()
    data = response.json()
    assert data["id"] == str(submission.pk)

    schema_tester.validate_response(response=response)


@pytest.mark.django_db
def test_submission_retrieve_api__unprocessed_not_accessible(
    superuser_client: APIClient,
):
    submission = SubmissionFactory(is_processed=False)
    url = reverse("submission-api-detail", args=(submission.pk,))
    response = superuser_client.get(url)
    assert response.status_code == 404, response.json()


@pytest.mark.django_db
@pytest.mark.parametrize(
    "user_name, assigned_as, expected_status",
    [
        ("unprivileged_user", CaseRole.NONE, 403),
        ("unprivileged_user", CaseRole.PARALEGAL, 403),
        ("unprivileged_user", CaseRole.LAWYER, 403),
        ("paralegal_user", CaseRole.NONE, 403),
        ("paralegal_user", CaseRole.PARALEGAL, 200),
        ("paralegal_user", CaseRole.LAWYER, 403),
        ("lawyer_user", CaseRole.NONE, 403),
        ("lawyer_user", CaseRole.PARALEGAL, 200),
        ("lawyer_user", CaseRole.LAWYER, 200),
        ("coordinator_user", CaseRole.NONE, 200),
        ("coordinator_user", CaseRole.PARALEGAL, 200),
        ("coordinator_user", CaseRole.LAWYER, 200),
        ("admin_user", CaseRole.NONE, 200),
        ("admin_user", CaseRole.PARALEGAL, 200),
        ("admin_user", CaseRole.LAWYER, 200),
    ],
)
def test_submission_api_retrieve_perms(
    user_name: str,
    assigned_as: CaseRole,
    expected_status: int,
    user_client,
    request,
):
    """
    Test retrieve API perms for different users.
    """
    user = request.getfixturevalue(user_name)
    submission = SubmissionFactory(is_processed=True)
    issue = IssueFactory(submission=submission)

    if assigned_as == CaseRole.PARALEGAL:
        issue.paralegal = user
        issue.save()
    elif assigned_as == CaseRole.LAWYER:
        issue.lawyer = user
        issue.save()

    url = reverse("submission-api-detail", args=(submission.pk,))
    response = user_client.get(url)
    assert response.status_code == expected_status


@pytest.mark.django_db
@pytest.mark.parametrize(
    "user_name, assigned_as, expected_status",
    [
        ("unprivileged_user", CaseRole.NONE, 403),
        ("unprivileged_user", CaseRole.PARALEGAL, 403),
        ("unprivileged_user", CaseRole.LAWYER, 403),
        ("paralegal_user", CaseRole.NONE, 404),
        ("paralegal_user", CaseRole.PARALEGAL, 404),
        ("paralegal_user", CaseRole.LAWYER, 404),
        ("lawyer_user", CaseRole.NONE, 404),
        ("lawyer_user", CaseRole.PARALEGAL, 404),
        ("lawyer_user", CaseRole.LAWYER, 404),
        ("coordinator_user", CaseRole.NONE, 404),
        ("coordinator_user", CaseRole.PARALEGAL, 404),
        ("coordinator_user", CaseRole.LAWYER, 404),
        ("admin_user", CaseRole.NONE, 404),
        ("admin_user", CaseRole.PARALEGAL, 404),
        ("admin_user", CaseRole.LAWYER, 404),
    ],
)
def test_submission_api_retrieve_perms__unprocessed(
    user_name: str,
    assigned_as: CaseRole,
    expected_status: int,
    user_client,
    request,
):
    """
    Test retrieve API perms for different users with unprocessed submissions.
    """
    user = request.getfixturevalue(user_name)
    submission = SubmissionFactory(is_processed=False)
    issue = IssueFactory(submission=submission)

    if assigned_as == CaseRole.PARALEGAL:
        issue.paralegal = user
        issue.save()
    elif assigned_as == CaseRole.LAWYER:
        issue.lawyer = user
        issue.save()

    url = reverse("submission-api-detail", args=(submission.pk,))
    response = user_client.get(url)
    assert response.status_code == expected_status
