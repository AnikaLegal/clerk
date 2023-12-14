import pytest
from django.core.files.base import File
from django.utils import timezone, dateformat
from override_storage import override_storage
from tempfile import NamedTemporaryFile

from office.closure.service import (
    get_closure,
    get_closure_call,
    get_closure_email,
    get_closure_notice,
    DATE_FORMAT,
)
from office.factories import ClosureFactory, ClosureTemplateFactory
from office.models import Closure


YESTERDAY = timezone.now() - timezone.timedelta(days=1)
TODAY = timezone.now()
TOMORROW = timezone.now() + timezone.timedelta(days=1)

TEST_TEXT = """
The following placeholders should be replaced with the
corresponding dates from the closure: {close_date} {reopen_date}
"""


def _get_file(suffix):
    file = NamedTemporaryFile(suffix=suffix)
    return File(file, name=file.name)


def _format(closure: Closure, text: str) -> str:
    close = dateformat.format(closure.close_date, DATE_FORMAT)
    reopen = dateformat.format(closure.reopen_date, DATE_FORMAT)
    return text.format(close_date=close, reopen_date=reopen)


@pytest.mark.django_db
def test_get_closure_between_dates():
    expected = Closure.objects.create(
        close_date=YESTERDAY,
        reopen_date=TOMORROW,
    )
    assert get_closure() == expected


@pytest.mark.django_db
def test_get_closure_on_close_date():
    expected = Closure.objects.create(
        close_date=TODAY,
        reopen_date=TOMORROW,
    )
    assert get_closure() == expected


@pytest.mark.django_db
def test_do_not_get_closure_on_reopen_date():
    Closure.objects.create(
        close_date=YESTERDAY,
        reopen_date=TODAY,
    )
    assert get_closure() == None


@override_storage()
@pytest.mark.django_db
def test_get_closure_call():
    expected = ClosureFactory(call_audio=_get_file(".wav"))
    call_info = get_closure_call()
    assert expected.call_audio.name == call_info.audio
    assert expected.template.call_text == call_info.text


@pytest.mark.django_db
def test_get_closure_call_format():
    template = ClosureTemplateFactory(call_text=TEST_TEXT)
    expected = ClosureFactory(template=template)
    call_info = get_closure_call()
    assert _format(expected, TEST_TEXT) == call_info.text


@pytest.mark.django_db
def test_get_closure_email():
    expected = ClosureFactory()
    email = get_closure_email()
    assert expected.template.email_html == email


@pytest.mark.django_db
def test_get_closure_email_format():
    template = ClosureTemplateFactory(email_html=TEST_TEXT)
    expected = ClosureFactory(template=template)
    email = get_closure_email()
    assert _format(expected, TEST_TEXT) == email


@pytest.mark.django_db
def test_get_closure_notice():
    expected = ClosureFactory()
    notice = get_closure_notice()
    assert expected.template.notice_html == notice


@pytest.mark.django_db
def test_get_closure_email_format():
    template = ClosureTemplateFactory(notice_html=TEST_TEXT)
    expected = ClosureFactory(template=template)
    notice = get_closure_notice()
    assert _format(expected, TEST_TEXT) == notice
