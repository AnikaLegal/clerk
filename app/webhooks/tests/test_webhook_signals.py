from unittest import mock

import pytest

from webhooks.factories import WebflowContactFactory
from webhooks.services.slack import send_webflow_contact_slack

from blacklist.models import Blacklist
from webhooks.signals.webflow_contact import BLACKLIST_COMMENT


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


@pytest.mark.django_db
@pytest.mark.enable_signals
@mock.patch("webhooks.signals.webflow_contact.async_task", autospec=True)
def test_blacklisted_contact(mock_async):
    contact = WebflowContactFactory()
    Blacklist.objects.create(email=contact.email)

    assert not contact.is_alert_sent
    mock_async.assert_not_called()
    # Save the contact to trigger signal.
    contact.save()

    # Ensure nothing was sent
    mock_async.assert_not_called()

    # Ensure the contact properties are correct
    assert not contact.requires_callback
    assert contact.comments == BLACKLIST_COMMENT
