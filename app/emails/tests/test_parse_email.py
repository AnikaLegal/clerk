from io import BytesIO

import pytest
from django.core.files.uploadedfile import InMemoryUploadedFile
from django.utils.datastructures import MultiValueDict

from emails.models import Email, EmailAttachment, EmailState
from emails.service import process_inbound_email


@pytest.mark.django_db
def test_parse_email__with_no_files():
    data = {
        "subject": ["Hello World!"],
        "envelope": [
            '{"to":["foo@em7221.test-mail.anikalegal.com"],"from":"matt@anikalegal.com"}'
        ],
        "to": [
            "foo@em7221.test-mail.anikalegal.com, bar@em7221.test-mail.anikalegal.com,  joe blow <joe@gmail.com>"
        ],
        "text": [
            "Hi Matt\r\n\r\nOn Sun, Jul 18, 2021 at 12:51 PM Matt Segal <matt@anikalegal.com> wrote:\r\n\r\n> hmmm\r\n>\r\n> --\r\n>\r\n> Matthew Segal\r\n>\r\n> Head of Technology\r\n>\r\n> mobile: 0431 417 373\r\n>\r\n> email: matt@anikalegal.com\r\n>\r\n> site: www.anikalegal.com\r\n>\r\n> Level 2/520 Bourke Street\r\n>\r\n> Melbourne VIC 3000\r\n>\n"
        ],
        "html": ["<div><h1>Hello World</h1></div>"],
    }
    files = {}
    assert Email.objects.count() == 0
    process_inbound_email(MultiValueDict(data), MultiValueDict(files))
    assert Email.objects.count() == 1
    email = Email.objects.last()
    assert email.from_addr == "matt@anikalegal.com"
    assert email.to_addr == "foo@em7221.test-mail.anikalegal.com"
    assert (
        email.to_addrs
        == "foo@em7221.test-mail.anikalegal.com, bar@em7221.test-mail.anikalegal.com,  joe blow <joe@gmail.com>"
    )
    assert email.cc_addrs == ""
    assert email.subject == "Hello World!"
    assert email.state == EmailState.RECEIVED
    assert (
        email.text
        == "Hi Matt\n\nOn Sun, Jul 18, 2021 at 12:51 PM Matt Segal <matt@anikalegal.com> wrote:\n\n> hmmm\n>\n> --\n>\n> Matthew Segal\n>\n> Head of Technology\n>\n> mobile: 0431 417 373\n>\n> email: matt@anikalegal.com\n>\n> site: www.anikalegal.com\n>\n> Level 2/520 Bourke Street\n>\n> Melbourne VIC 3000\n>\n"
    )
    assert email.html == "<div><h1>Hello World</h1></div>"


@pytest.mark.django_db
def test_parse_email__with_cc_addresses():
    data = {
        "subject": ["Hello World!"],
        "envelope": [
            '{"to":["foo@em7221.test-mail.anikalegal.com"],"from":"matt@anikalegal.com"}'
        ],
        "cc": ["bar@em7221.test-mail.anikalegal.com"],
        "to": [
            "foo@em7221.test-mail.anikalegal.com, bar@em7221.test-mail.anikalegal.com,  joe blow <joe@gmail.com>"
        ],
        "text": [
            "Hi Matt\r\n\r\nOn Sun, Jul 18, 2021 at 12:51 PM Matt Segal <matt@anikalegal.com> wrote:\r\n\r\n> hmmm\r\n>\r\n> --\r\n>\r\n> Matthew Segal\r\n>\r\n> Head of Technology\r\n>\r\n> mobile: 0431 417 373\r\n>\r\n> email: matt@anikalegal.com\r\n>\r\n> site: www.anikalegal.com\r\n>\r\n> Level 2/520 Bourke Street\r\n>\r\n> Melbourne VIC 3000\r\n>\n"
        ],
        "html": ["<div><h1>Hello World</h1></div>"],
    }
    files = {}
    assert Email.objects.count() == 0
    process_inbound_email(MultiValueDict(data), MultiValueDict(files))
    assert Email.objects.count() == 1
    email = Email.objects.last()
    assert email.from_addr == "matt@anikalegal.com"
    assert email.to_addr == "foo@em7221.test-mail.anikalegal.com"
    assert (
        email.to_addrs
        == "foo@em7221.test-mail.anikalegal.com, bar@em7221.test-mail.anikalegal.com,  joe blow <joe@gmail.com>"
    )
    assert email.cc_addrs == "bar@em7221.test-mail.anikalegal.com"
    assert email.subject == "Hello World!"
    assert email.state == EmailState.RECEIVED
    assert (
        email.text
        == "Hi Matt\n\nOn Sun, Jul 18, 2021 at 12:51 PM Matt Segal <matt@anikalegal.com> wrote:\n\n> hmmm\n>\n> --\n>\n> Matthew Segal\n>\n> Head of Technology\n>\n> mobile: 0431 417 373\n>\n> email: matt@anikalegal.com\n>\n> site: www.anikalegal.com\n>\n> Level 2/520 Bourke Street\n>\n> Melbourne VIC 3000\n>\n"
    )
    assert email.html == "<div><h1>Hello World</h1></div>"


@pytest.mark.django_db
def test_parse_email__with_files(settings, tmpdir):
    settings.MEDIA_ROOT = str(tmpdir)
    data = {
        "subject": ["Hello World!"],
        "envelope": [
            '{"to":["foo@em7221.test-mail.anikalegal.com"],"from":"matt@anikalegal.com"}'
        ],
        "to": ["foo@em7221.test-mail.anikalegal.com"],
        "text": ["Hi Matt\n"],
    }
    text_bytes = BytesIO("This is the file contents".encode("utf-8"))
    files = {
        "attachment1": [
            InMemoryUploadedFile(
                text_bytes,
                field_name="blank",
                size=25,
                name="foo.txt",
                charset="UTF-8",
                content_type="text/plain",
            )
        ]
    }
    assert EmailAttachment.objects.count() == 0
    assert Email.objects.count() == 0
    process_inbound_email(MultiValueDict(data), MultiValueDict(files))
    assert Email.objects.count() == 1
    email = Email.objects.last()
    assert email.from_addr == "matt@anikalegal.com"
    assert email.to_addr == "foo@em7221.test-mail.anikalegal.com"
    assert email.to_addrs == "foo@em7221.test-mail.anikalegal.com"
    assert email.subject == "Hello World!"
    assert email.state == EmailState.RECEIVED
    assert email.text == "Hi Matt\n"

    assert EmailAttachment.objects.count() == 1
    attach = EmailAttachment.objects.last()
    assert attach.email_id == email.pk
    assert (
        attach.file.name
        == f"email-attachments/d11e110ae03fcfe315ca3e20c9a82db7/foo.txt"
    )
    assert attach.content_type == "text/plain"
    assert attach.file.read() == b"This is the file contents"
