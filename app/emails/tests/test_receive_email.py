import os

import pytest
from emails.factories import ReceivedEmailFactory
from emails.models import (
    Email,
    EmailAttachment,
    EmailState,
    ReceivedAttachment,
    ReceivedEmail,
)
from emails.service.receive import receive_email_task


@pytest.mark.django_db
def test_receive_email_task_creates_email_and_attachments(settings, tmpdir):
    settings.MEDIA_ROOT = str(tmpdir)
    received_email = ReceivedEmailFactory()
    received_attachments = list(received_email.attachments.all())

    assert ReceivedEmail.objects.count() == 1
    assert ReceivedAttachment.objects.count() == len(received_attachments)
    assert Email.objects.count() == 0
    assert EmailAttachment.objects.count() == 0

    receive_email_task(received_email.pk)

    assert Email.objects.count() == 1
    email = Email.objects.last()
    assert email.state == EmailState.RECEIVED
    assert email.received_data == received_email.received_data

    assert EmailAttachment.objects.count() == len(received_attachments)

    for received_attachment in received_attachments:
        email_attachment = EmailAttachment.objects.get(
            file__endswith=received_attachment.name
        )
        assert email_attachment.email == email
        assert email_attachment.content_type == received_attachment.content_type
        assert email_attachment.file.read() == received_attachment.file.read()

    assert ReceivedEmail.objects.count() == 0
    assert ReceivedAttachment.objects.count() == 0


@pytest.mark.django_db
@pytest.mark.enable_signals
def test_deleting_received_email_cleans_local_files(
    settings, tmpdir, django_capture_on_commit_callbacks
):
    settings.MEDIA_ROOT = str(tmpdir)
    received_email = ReceivedEmailFactory()
    received_attachments = list(received_email.attachments.all())

    assert ReceivedEmail.objects.count() == 1
    assert ReceivedAttachment.objects.count() == len(received_attachments)

    with django_capture_on_commit_callbacks(execute=True):
        received_email.delete()

    assert ReceivedEmail.objects.count() == 0
    assert ReceivedAttachment.objects.count() == 0

    for received_attachment in received_attachments:
        assert not os.path.exists(received_attachment.file.path)
