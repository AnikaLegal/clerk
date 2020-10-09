from mailchimp3.mailchimpclient import MailChimpError
from mailchimp3.helpers import check_email

from django.utils import timezone
from django.conf import settings

from unittest import mock
import pytest

from core.factories import IssueFactory, ClientFactory
from core.services.mailchimp import remind_incomplete, find_clients
from core.models import CaseTopic


# Sample answers for testing
answers_with_email = [
    {"name": "CLIENT_NAME", "answer": "Michael Jordan"},
    {"name": "CLIENT_RENTAL_ADDRESS", "answer": "Chicago Bulls"},
    {"name": "CLIENT_DOB", "answer": "1963-02-17"},
    {"name": "CLIENT_EMAIL", "answer": "michael@jordan.com"},
    {"name": "CLIENT_PHONE", "answer": "4458 4858"},
]

answers_no_email = [
    {"name": "CLIENT_NAME", "answer": "Paul Scholes"},
    {"name": "CLIENT_RENTAL_ADDRESS", "answer": "Manchester United"},
    {"name": "CLIENT_DOB", "answer": "1974-11-16"},
    {"name": "CLIENT_PHONE", "answer": "4567 4756"},
]

answers_invalid_email = [
    {"name": "CLIENT_NAME", "answer": "Orenthal James Simpson"},
    {"name": "CLIENT_RENTAL_ADDRESS", "answer": "Buffalo Bills"},
    {"name": "CLIENT_DOB", "answer": "1947-07-09"},
    {"name": "CLIENT_EMAIL", "answer": "it_wasn't_me"},
    {"name": "CLIENT_PHONE", "answer": "4768 4858"},
]

# Sample dates for testing
THREE_WEEKS_AGO = timezone.now() - timezone.timedelta(days=21)
THREE_DAYS_AGO = timezone.now() - timezone.timedelta(days=3)
ONE_DAY_AGO = timezone.now() - timezone.timedelta(days=1)


@pytest.mark.django_db
def test_find_clients__with_success():
    client = ClientFactory(is_reminder_sent=False)
    sub = IssueFactory(
        client=client,
        is_submitted=False,
        topic=CaseTopic.REPAIRS,
        created_at=THREE_DAYS_AGO,
    )
    clients = find_clients(CaseTopic.REPAIRS)
    assert clients == [[sub, client]]
    clients = find_clients(CaseTopic.RENT_REDUCTION)
    assert clients == []


@pytest.mark.django_db
def test_find_clients__with_multiple_issues():
    client = ClientFactory(is_reminder_sent=False)
    IssueFactory(
        client=client,
        is_submitted=False,
        topic=CaseTopic.RENT_REDUCTION,
        created_at=THREE_DAYS_AGO,
    )
    latest_sub = IssueFactory(
        client=client,
        is_submitted=False,
        topic=CaseTopic.RENT_REDUCTION,
        created_at=THREE_DAYS_AGO,
    )
    clients = find_clients(CaseTopic.RENT_REDUCTION)
    assert clients == [[latest_sub, client]]
    clients = find_clients(CaseTopic.REPAIRS)
    assert clients == []


@pytest.mark.django_db
def test_find_clients__with_no_issues():
    client = ClientFactory(is_reminder_sent=False)
    clients = find_clients(CaseTopic.REPAIRS)
    assert clients == []


@pytest.mark.django_db
def test_find_clients__with_issue_complete():
    client = ClientFactory(is_reminder_sent=False)
    # Complete - should result in no results
    IssueFactory(
        client=client,
        is_submitted=True,
        topic=CaseTopic.REPAIRS,
        created_at=THREE_DAYS_AGO,
    )
    # Incomplete
    IssueFactory(
        client=client,
        is_submitted=False,
        topic=CaseTopic.REPAIRS,
        created_at=THREE_DAYS_AGO,
    )
    clients = find_clients(CaseTopic.REPAIRS)
    assert clients == []


@pytest.mark.django_db
def test_find_clients__with_reminder_already_sent():
    client = ClientFactory(is_reminder_sent=True)
    sub = IssueFactory(
        client=client,
        is_submitted=False,
        topic=CaseTopic.REPAIRS,
        created_at=THREE_DAYS_AGO,
    )
    clients = find_clients(CaseTopic.REPAIRS)
    assert clients == []


@pytest.mark.django_db
def test_find_clients__with_issue_too_early():
    client = ClientFactory(is_reminder_sent=False)
    sub = IssueFactory(
        client=client,
        is_submitted=False,
        topic=CaseTopic.REPAIRS,
        created_at=ONE_DAY_AGO,
    )
    clients = find_clients(CaseTopic.REPAIRS)
    assert clients == []


@pytest.mark.django_db
def test_find_clients__with_issue_too_late():
    client = ClientFactory(is_reminder_sent=False)
    sub = IssueFactory(
        client=client,
        is_submitted=False,
        topic=CaseTopic.REPAIRS,
        created_at=THREE_WEEKS_AGO,
    )
    clients = find_clients(CaseTopic.REPAIRS)
    assert clients == []


@pytest.mark.django_db
@mock.patch("core.services.mailchimp.MailChimp")
def test_remind_incomplete__sends_email(mock_api):
    # Setup a client who should be sent an email.
    client = ClientFactory(is_reminder_sent=False)
    sub = IssueFactory(
        client=client,
        is_submitted=False,
        topic=CaseTopic.REPAIRS,
        created_at=THREE_DAYS_AGO,
    )
    # Run task.
    mock_mailchimp = mock.Mock()
    mock_api.return_value = mock_mailchimp
    remind_incomplete()
    # Check that email was sent.
    expected_data = {
        "email_address": client.email,
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
    client.refresh_from_db()
    assert client.is_reminder_sent == True


@pytest.mark.django_db
@mock.patch("core.services.mailchimp.MailChimp")
def test_remind_incomplete_same_email(mock_api):
    # Setup a duplicate client who should be sent an email.
    client_a = ClientFactory(email="foo@bar.com", is_reminder_sent=False)
    sub_a = IssueFactory(
        client=client_a,
        is_submitted=False,
        topic=CaseTopic.REPAIRS,
        created_at=THREE_DAYS_AGO,
    )
    client_b = ClientFactory(email="foo@bar.com", is_reminder_sent=False)
    sub_b = IssueFactory(
        client=client_b,
        is_submitted=False,
        topic=CaseTopic.REPAIRS,
        created_at=THREE_DAYS_AGO,
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
    client_a.refresh_from_db()
    client_b.refresh_from_db()
    assert client_a.is_reminder_sent == True
    assert client_b.is_reminder_sent == False


@mock.patch("core.services.mailchimp.MailChimp")
@pytest.mark.django_db
def test_remind_incomplete_invalid_email(mock_api):
    # Setup two clients, one with an invalid who should be sent email.
    client_a = ClientFactory(email="@bar.com", is_reminder_sent=False)
    sub_a = IssueFactory(
        client=client_a,
        is_submitted=False,
        topic=CaseTopic.REPAIRS,
        created_at=THREE_DAYS_AGO,
    )
    client_b = ClientFactory(email="foo@bar.com", is_reminder_sent=False)
    sub_b = IssueFactory(
        client=client_b,
        is_submitted=False,
        topic=CaseTopic.REPAIRS,
        created_at=THREE_DAYS_AGO,
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
    client_a.refresh_from_db()
    client_b.refresh_from_db()
    assert client_a.is_reminder_sent == False
    assert client_b.is_reminder_sent == True
