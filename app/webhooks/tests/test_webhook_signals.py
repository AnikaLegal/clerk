from unittest import mock

import pytest

from webhooks.factories import WebflowContactFactory
from webhooks.services.slack import send_webflow_contact_slack


@pytest.mark.django_db
@pytest.mark.enable_signals
@mock.patch("webhooks.signals.webflow_contact.async_task", autospec=True)
def test_slack_sent_on_save(mock_async):
    contact = WebflowContactFactory()
    assert not contact.is_alert_sent
    mock_async.assert_not_called()
    # Save the contact to trigger signal.
    contact.save()
    # Ensure tasks were dispatched
    mock_async.assert_has_calls(
        [mock.call(send_webflow_contact_slack, str(contact.pk))]
    )


@pytest.mark.django_db
@pytest.mark.enable_signals
@mock.patch("webhooks.signals.webflow_contact.async_task", autospec=True)
def test_nothing_sent_when_already_sent(mock_async):
    contact = WebflowContactFactory(is_alert_sent=True)
    assert contact.is_alert_sent
    mock_async.assert_not_called()
    # Save the contact to trigger signal.
    contact.save()
    # Ensure nothing was sent
    mock_async.assert_not_called()
