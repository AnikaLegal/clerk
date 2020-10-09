from unittest import mock

import pytest
from django.conf import settings

from webhooks.services import slack
from webhooks.services.slack import send_webflow_contact_slack
from webhooks.factories import WebflowContactFactory
from webhooks.models import WebflowContact


@pytest.mark.django_db
def test_slack_webflow_msg(monkeypatch):
    """
    Ensure we call Slack without anything exploding
    """
    mock_send_msg = mock.Mock()
    monkeypatch.setattr(slack, "send_slack_message", mock_send_msg)
    contact = WebflowContactFactory()
    assert not contact.is_alert_sent
    mock_send_msg.assert_not_called()
    send_webflow_contact_slack(contact.pk)
    assert mock_send_msg.call_count == 1
    contact = WebflowContact.objects.get(pk=contact.id)
    assert contact.is_alert_sent
