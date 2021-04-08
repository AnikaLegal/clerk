from unittest import mock

import pytest
from django.conf import settings
from django.utils import timezone
from mailchimp3.helpers import check_email
from mailchimp3.mailchimpclient import MailChimpError

from core.factories import ClientFactory, IssueFactory
from core.models import CaseTopic, Submission
from core.services.mailchimp import find_submissions, remind_incomplete

# Sample dates for testing
THREE_WEEKS_AGO = timezone.now() - timezone.timedelta(days=21)
THREE_DAYS_AGO = timezone.now() - timezone.timedelta(days=3)
ONE_DAY_AGO = timezone.now() - timezone.timedelta(days=1)


@pytest.mark.django_db
def test_find_clients__with_success():
    sub = Submission.objects.create(
        answers={"EMAIL": "matt@gmail.com", "ISSUES": ["REPAIRS"]},
        created_at=THREE_DAYS_AGO,
        is_complete=False,
    )
    assert find_submissions(CaseTopic.REPAIRS) == [sub]
    assert find_submissions(CaseTopic.RENT_REDUCTION) == []


@pytest.mark.django_db
def test_find_clients__with_multiple_issues():
    sub1 = Submission.objects.create(
        answers={"EMAIL": "matt@gmail.com", "ISSUES": ["RENT_REDUCTION"]},
        created_at=THREE_DAYS_AGO,
        is_complete=False,
    )
    sub2 = Submission.objects.create(
        answers={"EMAIL": "matt@gmail.com", "ISSUES": ["RENT_REDUCTION"]},
        created_at=THREE_DAYS_AGO,
        is_complete=False,
    )
    assert find_submissions(CaseTopic.RENT_REDUCTION) == [sub1, sub2]
    assert find_submissions(CaseTopic.REPAIRS) == []


@pytest.mark.django_db
def test_find_clients__with_no_issues():
    Submission.objects.create(
        answers={"EMAIL": "matt@gmail.com", "ISSUES": []},
        created_at=THREE_DAYS_AGO,
        is_complete=False,
    )
    assert find_submissions(CaseTopic.REPAIRS) == []
    assert find_submissions(CaseTopic.RENT_REDUCTION) == []


@pytest.mark.django_db
def test_find_clients__with_issue_complete():
    Submission.objects.create(
        answers={"EMAIL": "matt@gmail.com", "ISSUES": ["RENT_REDUCTION"]},
        created_at=THREE_DAYS_AGO,
        is_complete=True,
    )
    sub2 = Submission.objects.create(
        answers={"EMAIL": "matt@gmail.com", "ISSUES": ["RENT_REDUCTION"]},
        created_at=THREE_DAYS_AGO,
        is_complete=False,
    )
    assert find_submissions(CaseTopic.RENT_REDUCTION) == [sub2]
    assert find_submissions(CaseTopic.REPAIRS) == []


@pytest.mark.django_db
def test_find_clients__with_reminder_already_sent():
    Submission.objects.create(
        answers={"EMAIL": "matt@gmail.com", "ISSUES": ["REPAIRS"]},
        created_at=THREE_DAYS_AGO,
        is_complete=False,
        is_reminder_sent=True,
    )
    assert find_submissions(CaseTopic.REPAIRS) == []


@pytest.mark.django_db
def test_find_clients__with_issue_too_early():
    Submission.objects.create(
        answers={"EMAIL": "matt@gmail.com", "ISSUES": ["REPAIRS"]},
        created_at=ONE_DAY_AGO,
        is_complete=False,
    )
    assert find_submissions(CaseTopic.REPAIRS) == []


@pytest.mark.django_db
def test_find_clients__with_issue_too_late():
    Submission.objects.create(
        answers={"EMAIL": "matt@gmail.com", "ISSUES": ["REPAIRS"]},
        created_at=THREE_WEEKS_AGO,
        is_complete=False,
    )
    assert find_submissions(CaseTopic.REPAIRS) == []


@pytest.mark.django_db
@mock.patch("core.services.mailchimp.MailChimp")
def test_remind_incomplete__sends_email(mock_api):
    # Setup a client who should be sent an email.
    sub = Submission.objects.create(
        answers={"EMAIL": "matt@gmail.com", "ISSUES": ["REPAIRS"]},
        created_at=THREE_DAYS_AGO,
        is_complete=False,
    )
    assert not sub.is_reminder_sent
    # Run task.
    mock_mailchimp = mock.Mock()
    mock_api.return_value = mock_mailchimp
    remind_incomplete()
    # Check that email was sent.
    expected_data = {
        "email_address": "matt@gmail.com",
        "status": "subscribed",
        "merge_fields": {"SUB_ID": str(sub.id)},
    }
    mock_api.assert_called_with(settings.MAILCHIMP_API_KEY)
    mock_mailchimp.lists.members.create.assert_called_with(
        list_id=settings.MAILCHIMP_REPAIRS_LIST_ID, data=expected_data
    )
    mock_mailchimp.automations.emails.queues.create.assert_called_with(
        workflow_id=settings.MAILCHIMP_REPAIRS_WORKFLOW_ID,
        email_id=settings.MAILCHIMP_REPAIRS_EMAIL_ID,
        data=expected_data,
    )
    sub.refresh_from_db()
    assert sub.is_reminder_sent


@pytest.mark.django_db
@mock.patch("core.services.mailchimp.MailChimp")
def test_remind_incomplete_same_email(mock_api):
    # Setup a duplicate client who should be sent an email.
    sub_a = Submission.objects.create(
        answers={"EMAIL": "matt@gmail.com", "ISSUES": ["REPAIRS"]},
        created_at=THREE_DAYS_AGO,
        is_complete=False,
    )
    sub_b = Submission.objects.create(
        answers={"EMAIL": "matt@gmail.com", "ISSUES": ["REPAIRS"]},
        created_at=THREE_DAYS_AGO,
        is_complete=False,
    )

    # Run the task.
    mock_mailchimp = mock.Mock()
    mock_api.return_value = mock_mailchimp
    emails = []

    def check(list_id, data):
        # MailChimp library an error if duplicate email detected.
        if data["email_address"] in emails:
            raise MailChimpError
        else:
            emails.append(data["email_address"])

    mock_mailchimp.lists.members.create.side_effect = check
    remind_incomplete()

    # Check the results
    sub_a.refresh_from_db()
    sub_b.refresh_from_db()
    assert sub_a.is_reminder_sent == True
    assert sub_b.is_reminder_sent == False


@mock.patch("core.services.mailchimp.MailChimp")
@pytest.mark.django_db
def test_remind_incomplete_invalid_email(mock_api):
    # Setup two clients, one with an invalid who should be sent email.
    sub_a = Submission.objects.create(
        answers={"EMAIL": "@gmail.com", "ISSUES": ["REPAIRS"]},
        created_at=THREE_DAYS_AGO,
        is_complete=False,
    )
    sub_b = Submission.objects.create(
        answers={"EMAIL": "matt@gmail.com", "ISSUES": ["REPAIRS"]},
        created_at=THREE_DAYS_AGO,
        is_complete=False,
    )

    # Run the task.
    mock_mailchimp = mock.Mock()
    mock_api.return_value = mock_mailchimp
    emails = []

    def check(list_id, data):
        # MailChimp check email.
        check_email(data["email_address"])

    mock_mailchimp.lists.members.create.side_effect = check
    remind_incomplete()

    # Check the results
    sub_a.refresh_from_db()
    sub_b.refresh_from_db()
    assert sub_a.is_reminder_sent == False
    assert sub_b.is_reminder_sent == True
