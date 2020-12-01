import pytest
from django.urls import reverse

from core.models import Submission, FileUpload
from core.factories import (
    get_dummy_file,
    IssueFactory,
    FileUploadFactory,
)


@pytest.mark.django_db
def test_file_upload_create(client):
    """
    User can upload a file which is associated with an issue.
    """
    issue = IssueFactory()
    list_url = reverse("upload-list")
    assert FileUpload.objects.count() == 0
    f = get_dummy_file("doc.pdf")
    resp = client.post(list_url, {"file": f, "issue": str(issue.id)})
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
def test_submission_views(client):
    """
    User can create, get, update and submit a submission.
    """
    # Try to list submissions - this should fail coz not allowed
    url = reverse("submission-list")
    # assert client.get(url).status_code == 405

    # Create a submission
    data = {"answers": {"FOO": "bar"}}
    resp = client.post(url, data=data, content_type="application/json")
    assert resp.status_code == 201
    sub = Submission.objects.last()
    sub_id = sub.id
    assert sub.answers == {"FOO": "bar"}
    assert not sub.is_complete

    # Get the created submission
    url = reverse("submission-detail", kwargs={"pk": sub_id})
    resp = client.get(url, content_type="application/json")
    resp.data == {"id": sub_id, "answers": sub.answers}

    # Try to delete the submission - this should fail coz not allowed.
    assert client.delete(url).status_code == 405

    # Update the submission answers
    data = {"answers": {"FOO": "bar", "BAZ": 1}}
    resp = client.patch(url, data=data, content_type="application/json")
    sub.refresh_from_db()
    assert sub.answers == {"FOO": "bar", "BAZ": 1}
    assert not sub.is_complete

    # Submit the submission
    url = reverse("submission-submit", kwargs={"pk": sub_id})
    resp = client.post(url, data={}, content_type="application/json")
    sub.refresh_from_db()
    assert sub.answers == {"FOO": "bar", "BAZ": 1}
    assert sub.is_complete

    # Try to get the submission - this should fail because it's already submitted.
    url = reverse("submission-detail", kwargs={"pk": sub_id})
    assert client.get(url).status_code == 403

    # Try to update - this should fail because it's already submitted.
    data = {"answers": {"FOO": "bar", "BAZ": 1}}
    resp = client.patch(url, data={}, content_type="application/json")
    assert resp.status_code == 403
    resp = client.put(url, data={}, content_type="application/json")
    assert resp.status_code == 403
