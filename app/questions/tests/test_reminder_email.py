from django.utils import timezone

from unittest import mock
import pytest

from questions.services.mailchimp import find_clients
from questions.tests.factories import SubmissionFactory


# sample answers for testing
answers_with_email = [{'name': 'CLIENT_NAME', 'answer': 'Michael Jordan'},
{'name': 'CLIENT_RENTAL_ADDRESS', 'answer': 'Chicago Bulls'},
{'name': 'CLIENT_DOB', 'answer': '1963-02-17'},
{'name': 'CLIENT_EMAIL', 'answer': 'michael@jordan.com'},
{'name': 'CLIENT_PHONE', 'answer': '4458 4858'}]

answers_no_email = [{'name': 'CLIENT_NAME', 'answer': 'Paul Scholes'},
{'name': 'CLIENT_RENTAL_ADDRESS', 'answer': 'Manchester United'},
{'name': 'CLIENT_DOB', 'answer': '1974-11-16'},
{'name': 'CLIENT_PHONE', 'answer': '4567 4756'}]

# sample dates for testing
three_weeks_ago = timezone.now() - timezone.timedelta(days=21)
three_days_ago = timezone.now() - timezone.timedelta(days=3)
one_day_ago = timezone.now() - timezone.timedelta(days=1)

# test find clients without emails
@pytest.mark.django_db
def test_no_emails():
    sub1 = SubmissionFactory(complete=False, is_reminder_sent=False, topic="COVID",
    created_at=three_days_ago, answers=answers_no_email)
    results = find_clients("COVID")
    assert results == []

# test find clients with email
@pytest.mark.django_db
def test_with_emails():
    sub1 = SubmissionFactory(complete=False, is_reminder_sent=False, topic="REPAIRS",
    created_at=three_days_ago, answers=answers_no_email)
    sub2 = SubmissionFactory(complete=False, is_reminder_sent=False, topic="REPAIRS",
    created_at=three_days_ago, answers=answers_with_email)
    results = find_clients("REPAIRS")
    assert len(results) == 1

# test find clients with irrelevant dates
@pytest.mark.django_db
def test_irrelevant_dates():
    sub1 = SubmissionFactory(complete=False, is_reminder_sent=False, topic="COVID",
    created_at=three_weeks_ago, answers=answers_with_email)
    sub2 = SubmissionFactory(complete=False, is_reminder_sent=False, topic="COVID",
    created_at=one_day_ago, answers=answers_with_email)
    results = find_clients("COVID")
    assert results == []

# test find clients with relevant dates
@pytest.mark.django_db
def test_relevant_dates():
    sub1 = SubmissionFactory(complete=False, is_reminder_sent=False, topic="REPAIRS",
    created_at=three_days_ago, answers=answers_with_email)
    sub2 = SubmissionFactory(complete=False, is_reminder_sent=False, topic="REPAIRS",
    created_at=three_days_ago, answers=answers_with_email)
    results = find_clients("REPAIRS")
    assert len(results) == 2