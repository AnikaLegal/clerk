import pytest
import pytz
from datetime import datetime

from core.factories import IssueFactory, EmailFactory
from emails.models import EmailState

from case.views.case.email import _get_email_threads, EmailThread


def dt(day):
    return datetime(2022, 1, day, tzinfo=pytz.UTC)


THREADED_EMAILS = [
    # Thread: R00956 Case Closure (emails 0-7)
    (EmailState.SENT, "R00956 Case Closure", dt(1)),
    (EmailState.SENT, " R00956 Case Closure ", dt(2)),
    (EmailState.RECEIVED, " Re: R00956 Case Closure", dt(3)),
    (EmailState.SENT, "Re: Re: R00956 Case Closure", dt(4)),
    (EmailState.RECEIVED, "Re:Re: R00956 Case Closure ", dt(5)),
    (EmailState.SENT, "R00956 case  closure", dt(6)),
    (EmailState.RECEIVED, "re: R00956 Case Closure", dt(7)),
    (EmailState.DRAFT, "R00956 Case Closure", dt(8)),
    # Thread: Legal advice (8-11)
    (EmailState.RECEIVED, "Legal Advice", dt(9)),
    (EmailState.SENT, "Legal Advice", dt(10)),
    (EmailState.RECEIVED, "legal advice", dt(11)),
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
    threads = _get_email_threads(issue)
    # Thread 0 - r00956-case-closure
    assert threads[0].subject == "R00956 Case Closure"
    assert threads[0].slug == "r00956-case-closure"
    assert threads[0].emails == emails[0:8]
    # Thread 1 - legal-advice
    assert threads[1].subject == "Legal Advice"
    assert threads[1].slug == "legal-advice"
    assert threads[1].emails == emails[8:12]
    # Thread 2 - a-quick-question
    assert threads[2].subject == "A quick question"
    assert threads[2].slug == "a-quick-question"
    assert threads[2].emails == emails[12:13]
