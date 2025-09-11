from unittest.mock import patch

import pytest
from core.services.slack import send_email_alert_slack, send_email_failure_alert_slack
from emails.models import Email, EmailState, ReceivedEmail
from emails.service import ingest_email_task, receive_email_task, send_email_task


@pytest.mark.django_db
@pytest.mark.enable_signals
@patch("emails.signals.async_task")
def test_save_email_ready_to_send_triggers_send_email_task(mock_async_task):
    email = Email.objects.create(state=EmailState.READY_TO_SEND)
    mock_async_task.assert_called_once_with(send_email_task, email.pk)


@pytest.mark.django_db
@pytest.mark.enable_signals
@patch("emails.signals.async_task")
def test_save_email_received_triggers_ingest_email_task(mock_async_task):
    email = Email.objects.create(state=EmailState.RECEIVED)
    mock_async_task.assert_called_once_with(ingest_email_task, email.pk)


@pytest.mark.django_db
@pytest.mark.enable_signals
@patch("emails.signals.async_task")
def test_save_email_ingested_and_no_alert_triggers_slack_alert(mock_async_task):
    email = Email.objects.create(state=EmailState.INGESTED, is_alert_sent=False)
    mock_async_task.assert_called_once_with(send_email_alert_slack, email.pk)


@pytest.mark.django_db
@pytest.mark.enable_signals
@patch("emails.signals.async_task")
def test_save_email_ingested_and_alert_sent_does_not_trigger_slack_alert(
    mock_async_task,
):
    Email.objects.create(state=EmailState.INGESTED, is_alert_sent=True)
    mock_async_task.assert_not_called()


@pytest.mark.django_db
@pytest.mark.enable_signals
@patch("emails.signals.async_task")
def test_save_email_delivery_failure_and_no_alert_triggers_failure_slack_alert(
    mock_async_task,
):
    email = Email.objects.create(state=EmailState.DELIVERY_FAILURE, is_alert_sent=False)
    mock_async_task.assert_called_once_with(send_email_failure_alert_slack, email.pk)


@pytest.mark.django_db
@pytest.mark.enable_signals
@patch("emails.signals.async_task")
def test_save_email_delivery_failure_and_alert_sent_does_not_trigger_failure_slack_alert(
    mock_async_task,
):
    Email.objects.create(state=EmailState.DELIVERY_FAILURE, is_alert_sent=True)
    mock_async_task.assert_not_called()


@pytest.mark.django_db(transaction=True)
@pytest.mark.enable_signals
@patch("emails.signals.async_task")
def test_post_save_received_email_triggers_receive_email_task(mock_async_task):
    received_email = ReceivedEmail.objects.create(received_data={})
    mock_async_task.assert_called_with(receive_email_task, received_email.pk)
