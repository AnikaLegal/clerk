"""
test
- permissions
- functionality
- schema
"""
import pytest
import pytz
from datetime import datetime

from core.factories import IssueFactory, EmailFactory
from emails.models import EmailState

from case.views.case_email import get_email_threads, EmailThread


def test_case_email_list_view():
    pass


def test_case_email_get_view():
    pass


def test_case_email_create_view():
    pass


def test_case_email_update_view():
    pass


def test_case_email_delete_view():
    pass


def test_case_email_add_attachment_view():
    pass


def test_case_email_delete_attachment_view():
    pass


def test_case_email_upload_attachment_to_sharepoint_view():
    pass


def test_case_email_download_attachment_from_sharepoint_view():
    pass


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
