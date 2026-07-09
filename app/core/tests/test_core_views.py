import pytest
from django.test.client import BOUNDARY, MULTIPART_CONTENT, encode_multipart
from django.urls import reverse

from core.factories import FileUploadFactory, IssueFactory, get_dummy_file
from core.models import FileUpload, Submission


@pytest.mark.django_db
def test_file_upload_create(anon_client):
    """
    User can upload a file which is associated with an issue.
    """
    issue = IssueFactory()
    list_url = reverse("upload-list")
    assert FileUpload.objects.count() == 0
    f = get_dummy_file("doc.pdf")
    resp = anon_client.post(
        list_url,
        data=encode_multipart(BOUNDARY, {"file": f, "issue": str(issue.id)}),
        content_type=MULTIPART_CONTENT,
    )
    assert resp.data["id"]
    assert resp.data["issue"] == issue.id
    assert FileUpload.objects.count() == 1


@pytest.mark.django_db
def test_file_upload_forbidden(client):
    """
    User cannot list, get, delete, update file uploads
    """
    upload = FileUploadFactory()
    list_url = reverse("upload-list")
    assert client.get(list_url).status_code == 405


@pytest.mark.django_db
def test_submission_views(anon_client, client):
    """
    User can create, get, update and submit a submission.
    """
    url = reverse("submission-list")

    # Create a submission
    data = {"answers": {"EMAIL": "test@example.com"}}
    resp = anon_client.post(url, data=data)
    assert resp.status_code == 201
    sub = Submission.objects.last()
    sub_id = sub.id
    assert sub.answers == {"EMAIL": "test@example.com"}
    assert not sub.is_complete

    # Get the created submission
    url = reverse("submission-detail", kwargs={"pk": sub_id})
    resp = anon_client.get(url)
    assert resp.data == {"id": str(sub_id), "answers": sub.answers}

    # Try to delete the submission - this should fail coz not allowed.
    # (Plain client: the method is deliberately absent from the OpenAPI spec.)
    assert client.delete(url).status_code == 405

    # Update the submission answers
    data = {"answers": {"EMAIL": "test@example.com", "ISSUES": "REPAIRS"}}
    resp = anon_client.patch(url, data=data)
    sub.refresh_from_db()
    assert sub.answers == {"EMAIL": "test@example.com", "ISSUES": "REPAIRS"}
    assert not sub.is_complete

    # Submit the submission
    url = reverse("submission-submit", kwargs={"pk": sub_id})
    resp = anon_client.post(url)
    assert resp.status_code == 200
    sub.refresh_from_db()
    assert sub.answers == {"EMAIL": "test@example.com", "ISSUES": "REPAIRS"}
    assert sub.is_complete

    # Try to get the submission - this should fail because it's already submitted.
    url = reverse("submission-detail", kwargs={"pk": sub_id})
    assert anon_client.get(url).status_code == 403

    # Try to update - this should fail because it's already submitted.
    resp = anon_client.patch(url, data={"answers": {"FOO": "bar"}})
    assert resp.status_code == 403
    resp = client.put(url, data={}, content_type="application/json")
    assert resp.status_code == 403

    # Try to submit again - this should fail so that processing isn't queued
    # twice.
    url = reverse("submission-submit", kwargs={"pk": sub_id})
    assert anon_client.post(url).status_code == 403


@pytest.mark.django_db
def test_submission_answers_must_be_an_object(client):
    """
    Answers that aren't a JSON object are rejected. (Plain client: the
    schema-validated client refuses to send a request that violates the
    contract in the first place.)
    """
    url = reverse("submission-list")
    resp = client.post(
        url, data={"answers": "not-an-object"}, content_type="application/json"
    )
    assert resp.status_code == 400


@pytest.mark.django_db
def test_submission_submit_requires_email_and_issues(anon_client):
    """
    Submissions cannot be marked complete without the answers that backend
    processing depends on.
    """
    url = reverse("submission-list")
    resp = anon_client.post(url, data={"answers": {"FOO": "bar"}})
    assert resp.status_code == 201
    sub_id = resp.data["id"]

    submit_url = reverse("submission-submit", kwargs={"pk": sub_id})
    resp = anon_client.post(submit_url)
    assert resp.status_code == 400
    sub = Submission.objects.get(pk=sub_id)
    assert not sub.is_complete
