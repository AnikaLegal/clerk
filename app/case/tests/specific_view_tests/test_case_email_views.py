"""
TODO: Test permissions
TODO: Test that emails actually get sent
"""
import pytz
from datetime import datetime
from io import StringIO
from unittest.mock import patch, Mock

import pytest
from rest_framework.test import APIClient
from rest_framework.reverse import reverse
from django.core.files.uploadedfile import InMemoryUploadedFile

from accounts.models import User
from core.factories import (
    IssueFactory,
    EmailFactory,
    EmailAttachmentFactory,
    get_dummy_file,
)
from emails.models import EmailState, Email, EmailAttachment
from case.views.case_email import get_email_threads, EmailThread
from conftest import schema_tester


@pytest.mark.django_db
def test_case_email_list_view(superuser_client: APIClient):
    issue = IssueFactory()
    for state, subject, created_at in THREADED_EMAILS:
        EmailFactory(issue=issue, state=state, subject=subject, created_at=created_at)

    url = reverse("email-api-detail", args=(issue.pk,))  # Actually a list view
    response = superuser_client.get(url)
    assert response.status_code == 200, response.json()
    threads = response.json()
    assert len(threads) == 3
    schema_tester.validate_response(response=response)


@pytest.mark.django_db
def test_case_email_get_view(superuser_client: APIClient):
    email = EmailFactory(state="DRAFT")
    url = reverse("email-api-email-detail", args=(email.issue.pk, email.pk))
    response = superuser_client.get(url)
    assert response.status_code == 200, response.json()
    email_data = response.json()
    assert email_data["id"] == email.pk
    schema_tester.validate_response(response=response)


@pytest.mark.django_db
def test_case_email_create_view(superuser_client: APIClient, superuser: User):
    email = EmailFactory()
    url = reverse("email-api-create", args=(email.issue.pk,))
    data = {
        "to_address": "foo@example.com",
        "cc_addresses": [],
        "subject": "Hello World",
        "text": "Hi there!",
        "html": "<p>Hi there!</p>",
    }
    response = superuser_client.post(url, data=data, format="json")
    assert response.status_code == 201, response.json()
    email_data = response.json()
    assert email_data["issue"] == str(email.issue.pk)
    assert email_data["sender"]["id"] == superuser.pk
    assert email_data["state"] == "DRAFT"
    assert email_data["from_address"].endswith("@fake.anikalegal.com")
    schema_tester.validate_response(response=response)


@pytest.mark.django_db
def test_case_email_update_view(superuser_client: APIClient):
    email = EmailFactory(state="DRAFT", subject="Hello World")
    url = reverse("email-api-email-detail", args=(email.issue.pk, email.pk))
    response = superuser_client.patch(
        url, data={"subject": "Goodbye All!"}, format="json"
    )
    assert response.status_code == 200, response.json()
    email_data = response.json()
    assert email_data["subject"] == "Goodbye All!"
    schema_tester.validate_response(response=response)


@pytest.mark.django_db
def test_case_email_delete_view(superuser_client: APIClient):
    email = EmailFactory(state="DRAFT")
    assert Email.objects.count() == 1
    url = reverse("email-api-email-detail", args=(email.issue.pk, email.pk))
    response = superuser_client.delete(url)
    assert response.status_code == 204
    assert Email.objects.count() == 0
    schema_tester.validate_response(response=response)


@pytest.mark.django_db
def test_case_email_add_attachment_view(superuser_client: APIClient):
    email = EmailFactory(state="DRAFT")
    url = reverse("email-api-attachment-create", args=(email.issue.pk, email.pk))
    uploaded_file = InMemoryUploadedFile(
        StringIO("Hello World!"),
        name="hello-world.txt",
        content_type="text/plain",
        field_name="file",
        size=12,
        charset="utf-8",
    )
    data = {"file": uploaded_file}
    response = superuser_client.post(url, data=data)
    assert response.status_code == 201, response.json()
    attach_data = response.json()
    assert attach_data["email"] == email.pk
    attachment = EmailAttachment.objects.get(pk=attach_data["id"])
    assert attachment.file.read() == b"Hello World!"
    schema_tester.validate_response(response=response)


@pytest.mark.django_db
def test_case_email_delete_attachment_view(superuser_client: APIClient):
    email = EmailFactory(state="DRAFT")
    f = get_dummy_file("image.png")
    attachment = EmailAttachmentFactory(email=email, file=f)
    assert EmailAttachment.objects.count() == 1
    url = reverse(
        "email-api-attachment-delete", args=(email.issue.pk, email.pk, attachment.pk)
    )
    response = superuser_client.delete(url)
    assert response.status_code == 204
    assert EmailAttachment.objects.count() == 0
    schema_tester.validate_response(response=response)


@pytest.mark.django_db
@patch("case.views.case_email.save_email_attachment")
def test_case_email_upload_attachment_to_sharepoint_view(
    mock_save_email_attachment, superuser_client: APIClient
):
    email = EmailFactory(state="DRAFT")
    f = get_dummy_file("image.png")
    attachment = EmailAttachmentFactory(email=email, file=f)
    url = reverse(
        "email-api-attachment-sharepoint-upload",
        args=(email.issue.pk, email.pk, attachment.pk),
    )
    response = superuser_client.post(url)
    mock_save_email_attachment.assert_called_once_with(email, attachment)
    schema_tester.validate_response(response=response)


@pytest.mark.django_db
@patch("case.views.case_email.MSGraphAPI")
def test_case_email_download_attachment_from_sharepoint_view(
    mock_microsoft_api, superuser_client: APIClient
):
    mock_api = Mock()
    mock_api.folder.download_file.return_value = (
        "hello.txt",
        "text/plain",
        b"Hello World!",
    )
    mock_microsoft_api.return_value = mock_api
    sharepoint_id = "ABCD-1234"

    email = EmailFactory(state="DRAFT")
    url = reverse(
        "email-api-attachment-sharepoint-download",
        args=(email.issue.pk, email.pk, sharepoint_id),
    )
    assert EmailAttachment.objects.count() == 0
    response = superuser_client.post(url)
    assert EmailAttachment.objects.count() == 1

    mock_api.folder.download_file.assert_called_once_with(sharepoint_id)
    attachment = EmailAttachment.objects.get()
    assert attachment.file.read() == b"Hello World!"
    schema_tester.validate_response(response=response)


def dt(day):
    return datetime(2022, 1, day, tzinfo=pytz.UTC)


THREADED_EMAILS = [
    # Thread: R00956 Case Closure (emails 0-7)
    (EmailState.SENT, "R00956 Case Closure", dt(1)),
    (EmailState.SENT, " R00956 Case Closure ", dt(2)),
    (EmailState.INGESTED, " Re: R00956 Case Closure", dt(3)),
    (EmailState.SENT, "Re: Re: R00956 Case Closure", dt(4)),
    (EmailState.INGESTED, "Re:Re: R00956 Case Closure ", dt(5)),
    (EmailState.SENT, "R00956 case  closure", dt(6)),
    (EmailState.INGESTED, "re: R00956 Case Closure", dt(7)),
    (EmailState.DRAFT, "R00956 Case Closure", dt(8)),
    # Thread: Legal advice (8-11)
    (EmailState.INGESTED, "Legal Advice", dt(9)),
    (EmailState.SENT, "Legal Advice", dt(10)),
    (EmailState.INGESTED, "legal advice", dt(11)),
    (EmailState.SENT, "Re: Legal advice", dt(12)),
    # Random draft (12)
    (EmailState.DRAFT, "A quick question", dt(14)),
]


def test_email_subject_slugify():
    assert [EmailThread.slugify_subject(e[1]) for e in THREADED_EMAILS] == [
        "r00956-case-closure",
        "r00956-case-closure",
        "r00956-case-closure",
        "r00956-case-closure",
        "r00956-case-closure",
        "r00956-case-closure",
        "r00956-case-closure",
        "r00956-case-closure",
        "legal-advice",
        "legal-advice",
        "legal-advice",
        "legal-advice",
        "a-quick-question",
    ]


@pytest.mark.django_db
def test_email_thread_aggregation():
    issue = IssueFactory()
    emails = [
        EmailFactory(issue=issue, state=state, subject=subject, created_at=created_at)
        for state, subject, created_at in THREADED_EMAILS
    ]
    threads = get_email_threads(issue)
    # Thread 2 - r00956-case-closure
    assert threads[2].subject == "R00956 Case Closure"
    assert threads[2].slug == "r00956-case-closure"
    assert threads[2].emails == list(reversed(emails[0:8]))
    # Thread 1 - legal-advice
    assert threads[1].subject == "Legal Advice"
    assert threads[1].slug == "legal-advice"
    assert threads[1].emails == list(reversed(emails[8:12]))
    # Thread 0 - a-quick-question
    assert threads[0].subject == "A quick question"
    assert threads[0].slug == "a-quick-question"
    assert threads[0].emails == list(reversed(emails[12:13]))
