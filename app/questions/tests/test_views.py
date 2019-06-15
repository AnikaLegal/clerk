import pytest
from django.urls import reverse

from questions.tests.factories import SubmissionFactory, ImageUploadFactory
from questions.models import Submission, ImageUpload
from .utils import get_dummy_file


@pytest.mark.django_db
def test_submission_create(client):
    """
    User can create a submission
    """
    url = reverse("submission-list")
    data = {"questions": {"foo": {"a": 1}}, "answers": []}
    resp = client.post(url, data=data, content_type="application/json")
    assert resp.status_code == 201
    sub = Submission.objects.last()
    assert resp.data == {"id": str(sub.id), "complete": False, **data}
    assert sub.answers == []
    assert sub.questions == {"foo": {"a": 1}}
    assert sub.complete == False


@pytest.mark.django_db
def test_submission_get(client):
    """
    User can retrieve a submission
    """
    sub = SubmissionFactory(questions={}, answers=[{"FOO": [1, 2, 3]}])
    url = reverse("submission-detail", args=[sub.id])
    resp = client.get(url)
    assert resp.status_code == 200
    assert resp.data == {
        "id": str(sub.id),
        "answers": [{"FOO": [1, 2, 3]}],
        "questions": {},
        "complete": False,
    }


@pytest.mark.django_db
def test_submission_update(client):
    """
    User can update a submission
    """
    sub = SubmissionFactory(questions={}, answers=[{"FOO": [1, 2, 3]}])
    url = reverse("submission-detail", args=[sub.id])
    update = {
        "answers": [{"BAR": "no"}],
        "questions": {"foo": {"a": 1}},
        "complete": True,
    }
    resp = client.patch(url, data=update, content_type="application/json")
    assert resp.status_code == 200
    assert resp.data == {
        "id": str(sub.id),
        "answers": [{"BAR": "no"}],
        "questions": {"foo": {"a": 1}},
        "complete": True,
    }
    sub.refresh_from_db()
    assert sub.questions == {"foo": {"a": 1}}
    assert sub.answers == [{"BAR": "no"}]
    assert sub.complete == True


@pytest.mark.django_db
def test_submission_update_fails_when_complete(client):
    """
    User cannot update a complete submission
    """
    sub = SubmissionFactory(answers=[{"FOO": [1, 2, 3]}], questions={}, complete=True)
    update = {"answers": [{"BAR": "no"}]}
    url = reverse("submission-detail", args=[sub.id])
    resp = client.patch(url, data=update, content_type="application/json")
    assert resp.status_code == 400


@pytest.mark.django_db
def test_submission_security(client):
    """
    User cannot list or delete submissions
    """
    sub = SubmissionFactory(questions={}, answers=[{"FOO": [1, 2, 3]}])
    list_url = reverse("submission-list")
    detail_url = reverse("submission-detail", args=[sub.id])

    # User cannot delete a submission
    resp = client.delete(detail_url)
    assert resp.status_code == 405

    # User cannot list submissions
    resp = client.get(list_url)
    assert resp.status_code == 405


@pytest.mark.django_db
def test_image_upload_create(client):
    """
    User can upload a file to create an image upload
    """
    list_url = reverse("images-list")
    assert ImageUpload.objects.count() == 0
    f = get_dummy_file("image.png")
    resp = client.post(list_url, {"image": f})
    assert resp.data["id"]
    assert ImageUpload.objects.count() == 1


@pytest.mark.django_db
def test_image_upload_security(client):
    """
    User cannot list, get, or delete image uploads
    """
    image_upload = ImageUploadFactory()
    list_url = reverse("images-list")
    detail_url = f"{list_url}{image_upload.id}/"

    # User cannot get an image
    resp = client.get(detail_url)
    assert resp.status_code == 404

    # User cannot update an image
    resp = client.patch(detail_url)
    assert resp.status_code == 404

    # User cannot delete a image
    resp = client.delete(detail_url)
    assert resp.status_code == 404

    # User cannot list images
    resp = client.get(list_url)
    assert resp.status_code == 405
