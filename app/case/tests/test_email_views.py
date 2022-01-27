import pytest

from core.factories import IssueFactory, EmailFactory
from emails.models import EmailState

from case.views.case.email import _get_email_threads, EmailThread

THREADED_EMAILS = [
    # Thread: R00956 Case Closure (emails 0-7)
    (EmailState.SENT, "R00956 Case Closure"),
    (EmailState.SENT, " R00956 Case Closure "),
    (EmailState.RECEIVED, " Re: R00956 Case Closure"),
    (EmailState.SENT, "Re: Re: R00956 Case Closure"),
    (EmailState.RECEIVED, "Re:Re: R00956 Case Closure "),
    (EmailState.SENT, "R00956 case  closure"),
    (EmailState.RECEIVED, "re: R00956 Case Closure"),
    (EmailState.DRAFT, "R00956 Case Closure"),
    # Thread: Legal advice (8-11)
    (EmailState.RECEIVED, "Legal Advice"),
    (EmailState.SENT, "Legal Advice"),
    (EmailState.RECEIVED, "legal advice"),
    (EmailState.SENT, "Re: Legal advice"),
    # Random draft (12)
    (EmailState.DRAFT, "A quick question"),
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
        EmailFactory(issue=issue, state=state, subject=subject)
        for state, subject in THREADED_EMAILS
    ]
    threads = _get_email_threads(issue)
    # Thread 0 - r00956-case-closure
    assert threads[0].subject == "R00956 Case Closure"
    assert threads[0].slug == "r00956-case-closure"
    assert threads[0].emails == emails[0:8]
    # Thread 1 - legal-advice
    # Thread 2 - a-quick-question
