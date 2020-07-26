from django.utils import timezone

from unittest import mock

import pytest

from questions.services.mailchimp import find_clients
from questions.tests.factories import SubmissionFactory
from questions.models import Submission


@pytest.mark.django_db
def test_find_clients():
    answers_with_email = [{'name': 'CLIENT_NAME', 'answer': 'Michael Jordan'},
    {'name': 'CLIENT_RENTAL_ADDRESS', 'answer': 'Bulls Street'},
    {'name': 'CLIENT_DOB', 'answer': '1967-3-12'},
    {'name': 'CLIENT_EMAIL', 'answer': 'michael@jordan.com'},
    {'name': 'CLIENT_PHONE', 'answer': '4458'}]

    answers_no_email = [{'name': 'CLIENT_NAME', 'answer': 'Juan Mata'},
    {'name': 'CLIENT_RENTAL_ADDRESS', 'answer': 'valencia'},
    {'name': 'CLIENT_DOB', 'answer': '1964-3-12'},
    {'name': 'CLIENT_PHONE', 'answer': '3487'}]

    three_weeks_ago = timezone.now() - timezone.timedelta(days=21)
    three_days_ago = timezone.now() - timezone.timedelta(days=3)
    one_day_ago = timezone.now() - timezone.timedelta(days=1)

    # positive
    sub1 = SubmissionFactory(complete=False, is_reminder_sent=False, created_at= three_days_ago, answers=answers_with_email)
    # negative because complete
    sub2 = SubmissionFactory(complete=True,  is_reminder_sent=False, created_at= three_weeks_ago, answers=answers_with_email)
    # negative because no email
    sub3 = SubmissionFactory(complete=False, is_reminder_sent=False, created_at = three_days_ago, answers=answers_no_email)


    results = find_clients()

    assert results == [sub1]
