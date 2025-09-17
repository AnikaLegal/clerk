"""
Test saving inbound emails.
TODO: Rewrite tests to test the view as well as the service functions.
"""

from io import BytesIO

import pytest
from django.core.files.uploadedfile import InMemoryUploadedFile
from django.utils.datastructures import MultiValueDict
from emails.models import Email, EmailAttachment
from emails.service import save_inbound_email

data = MultiValueDict(
    {
        "subject": ["Test subject"],
        "envelope": [{"to": ["to@example.com"], "from": "from@example.com"}],
        "to": ["to@example.com"],
        "text": ["Body text"],
        "html": ["<b>Body</b>"],
    }
)

file_1_content = BytesIO(b"Attachment 1 content")
file_1 = InMemoryUploadedFile(
    file_1_content,
    field_name="file",
    size=len(file_1_content.getvalue()),
    name="test_1.txt",
    charset="utf-8",
    content_type="text/plain",
)

file_2_content = BytesIO(b"Attachment 2 content")
file_2 = InMemoryUploadedFile(
    file_2_content,
    field_name="file",
    size=len(file_2_content.getvalue()),
    name="test_2.txt",
    charset="utf-8",
    content_type="text/plain",
)


@pytest.mark.django_db
def test_save_inbound_email_no_attachments():
    files = MultiValueDict()
    assert Email.objects.count() == 0
    assert EmailAttachment.objects.count() == 0

    save_inbound_email(data, files)

    assert Email.objects.count() == 1
    assert EmailAttachment.objects.count() == 0
    email = Email.objects.last()
    assert email.received_data == data.dict()


@pytest.mark.django_db
def test_save_inbound_email_with_single_attachment(settings, tmpdir):
    settings.MEDIA_ROOT = str(tmpdir)
    files = MultiValueDict({"attachment1": [file_1]})

    assert Email.objects.count() == 0
    assert EmailAttachment.objects.count() == 0

    save_inbound_email(data, files)

    assert Email.objects.count() == 1
    email = Email.objects.last()

    assert email.attachments.count() == 1
    attachment = email.attachments.first()
    assert attachment.content_type == file_1.content_type
    assert attachment.file.name.endswith(file_1.name)
    assert attachment.file.read() == file_1_content.getvalue()


@pytest.mark.django_db
def test_save_inbound_email_with_multiple_attachments(settings, tmpdir):
    settings.MEDIA_ROOT = str(tmpdir)
    files = MultiValueDict({"attachment1": [file_1], "attachment2": [file_2]})

    assert Email.objects.count() == 0
    assert EmailAttachment.objects.count() == 0

    save_inbound_email(data, files)

    assert Email.objects.count() == 1
    email = Email.objects.last()
    assert email.attachments.count() == 2

    attachment_1 = email.attachments.first()
    assert attachment_1.content_type == file_1.content_type
    assert attachment_1.file.name.endswith(file_1.name)
    assert attachment_1.file.read() == file_1_content.getvalue()

    attachment_2 = email.attachments.last()
    assert attachment_2.content_type == file_2.content_type
    assert attachment_2.file.name.endswith(file_2.name)
    assert attachment_2.file.read() == file_2_content.getvalue()


@pytest.mark.django_db
def test_save_inbound_email_with_duplicate_attachments(settings, tmpdir):
    settings.MEDIA_ROOT = str(tmpdir)
    files = MultiValueDict({"attachment1": [file_1], "attachment2": [file_1]})

    assert Email.objects.count() == 0
    assert EmailAttachment.objects.count() == 0

    save_inbound_email(data, files)

    assert Email.objects.count() == 1
    email = Email.objects.last()
    assert email.attachments.count() == 2

    attachment_1 = email.attachments.first()
    assert attachment_1.content_type == file_1.content_type
    assert attachment_1.file.name.endswith(file_1.name)
    assert attachment_1.file.read() == file_1_content.getvalue()

    attachment_2 = email.attachments.last()
    assert attachment_2.content_type == file_1.content_type
    # Note that the file name will be different due to how Django handles
    # duplicate file names.
    assert not attachment_2.file.name.endswith(file_1.name)
    assert attachment_2.file.read() == file_1_content.getvalue()
