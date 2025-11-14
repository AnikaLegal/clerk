import pytest
from conftest import schema_tester
from core.factories import SubmissionFactory, IssueFactory
from rest_framework.reverse import reverse
from rest_framework.test import APIClient


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
    "test_user, user_name, is_assigned, expected_status",
    [
        ("unassigned_user", "unprivileged_user", False, 403),
        ("assigned_user", "unprivileged_user", True, 403),
        ("unassigned_paralegal", "paralegal_user", False, 403),
        ("assigned_paralegal", "paralegal_user", True, 200),
        ("unassigned_coordinator", "coordinator_user", False, 200),
        ("assigned_coordinator", "coordinator_user", True, 200),
    ],
)
def test_submission_api_retrieve_perms(
    test_user: str,
    user_name: str,
    is_assigned: bool,
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

    if is_assigned:
        issue.paralegal = user
        issue.save()

    url = reverse("submission-api-detail", args=(submission.pk,))
    response = user_client.get(url)
    assert response.status_code == expected_status


@pytest.mark.django_db
@pytest.mark.parametrize(
    "test_user, user_name, is_assigned, expected_status",
    [
        ("unassigned_user", "unprivileged_user", False, 403),
        ("assigned_user", "unprivileged_user", True, 403),
        ("unassigned_paralegal", "paralegal_user", False, 404),
        ("assigned_paralegal", "paralegal_user", True, 404),
        ("unassigned_coordinator", "coordinator_user", False, 404),
        ("assigned_coordinator", "coordinator_user", True, 404),
    ],
)
def test_submission_api_retrieve_perms__unprocessed(
    test_user: str,
    user_name: str,
    is_assigned: bool,
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

    if is_assigned:
        issue.paralegal = user
        issue.save()

    url = reverse("submission-api-detail", args=(submission.pk,))
    response = user_client.get(url)
    assert response.status_code == expected_status
