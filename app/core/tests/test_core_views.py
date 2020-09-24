import pytest
from django.urls import reverse

from core.factories import get_dummy_file


@pytest.mark.skip
@pytest.mark.django_db
def test_issue_create(client):
    """
    User can create a issue
    """
    url = reverse("issue-list")
    data = {"questions": {"foo": {"a": 1}}, "answers": [], "topic": "REPAIRS"}
    resp = client.post(url, data=data, content_type="application/json")
    assert resp.status_code == 201
    sub = Issue.objects.last()
    assert resp.data == {"id": str(sub.id), "is_submitted": False, **data}
    assert sub.answers == []
    assert sub.questions == {"foo": {"a": 1}}
    assert sub.is_submitted == False


@pytest.mark.skip
@pytest.mark.django_db
def test_issue_get(client):
    """
    User can retrieve a issue
    """
    sub = IssueFactory(questions={}, answers=[{"FOO": [1, 2, 3]}], topic="REPAIRS")
    url = reverse("issue-detail", args=[sub.id])
    resp = client.get(url)
    assert resp.status_code == 200
    assert resp.data == {
        "id": str(sub.id),
        "topic": "REPAIRS",
        "answers": [{"FOO": [1, 2, 3]}],
        "questions": {},
        "is_submitted": False,
    }


@pytest.mark.skip
@pytest.mark.django_db
def test_issue_update(client):
    """
    User can update a issue
    """
    sub = IssueFactory(questions={}, answers=[{"FOO": [1, 2, 3]}], topic="REPAIRS")
    url = reverse("issue-detail", args=[sub.id])
    update = {
        "answers": [{"BAR": "no"}],
        "questions": {"foo": {"a": 1}},
        "is_submitted": True,
    }
    resp = client.patch(url, data=update, content_type="application/json")
    assert resp.status_code == 200
    assert resp.data == {
        "id": str(sub.id),
        "answers": [{"BAR": "no"}],
        "topic": "REPAIRS",
        "questions": {"foo": {"a": 1}},
        "is_submitted": True,
    }
    sub.refresh_from_db()
    assert sub.questions == {"foo": {"a": 1}}
    assert sub.answers == [{"BAR": "no"}]
    assert sub.is_submitted == True


@pytest.mark.skip
@pytest.mark.django_db
def test_issue_update_fails_when_is_submitted(client):
    """
    User cannot update a is_submitted issue
    """
    sub = IssueFactory(answers=[{"FOO": [1, 2, 3]}], questions={}, is_submitted=True)
    update = {"answers": [{"BAR": "no"}]}
    url = reverse("issue-detail", args=[sub.id])
    resp = client.patch(url, data=update, content_type="application/json")
    assert resp.status_code == 400


@pytest.mark.skip
@pytest.mark.django_db
def test_issue_security(client):
    """
    User cannot list or delete issues
    """
    sub = IssueFactory(questions={}, answers=[{"FOO": [1, 2, 3]}])
    list_url = reverse("issue-list")
    detail_url = reverse("issue-detail", args=[sub.id])

    # User cannot delete a issue
    resp = client.delete(detail_url)
    assert resp.status_code == 405

    # User cannot list issues
    resp = client.get(list_url)
    assert resp.status_code == 405


@pytest.mark.skip
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


@pytest.mark.skip
@pytest.mark.django_db
def test_file_upload_create(client):
    """
    User can upload a file to create an image upload
    """
    list_url = reverse("files-list")
    assert FileUpload.objects.count() == 0
    f = get_dummy_file("doc.pdf")
    resp = client.post(list_url, {"file": f})
    assert resp.data["id"]
    assert FileUpload.objects.count() == 1


@pytest.mark.skip
@pytest.mark.django_db
def test_file_upload_security(client):
    """
    User cannot list, get, or delete file uploads
    """
    file_upload = FileUploadFactory()
    list_url = reverse("files-list")
    detail_url = f"{list_url}{file_upload.id}/"

    # User cannot get an file
    resp = client.get(detail_url)
    assert resp.status_code == 404

    # User cannot update an file
    resp = client.patch(detail_url)
    assert resp.status_code == 404

    # User cannot delete a file
    resp = client.delete(detail_url)
    assert resp.status_code == 404

    # User cannot list files
    resp = client.get(list_url)
    assert resp.status_code == 405


@pytest.mark.skip
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
