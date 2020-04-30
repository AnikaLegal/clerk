import json
from unittest import mock

import pytest
import responses
from django.conf import settings

from webhooks.services.slack import send_webflow_contact_slack
from webhooks.tests.factories import WebflowContactFactory
from webhooks.models import WebflowContact


@pytest.mark.django_db
@responses.activate
def test_slack_webhook():
    """
    Ensure we call Slack without anything exploding
    https://github.com/getsentry/responses
    """
    contact = WebflowContactFactory()
    responses.add(
        method=responses.POST,
        url=settings.SUBMIT_SLACK_WEBHOOK_URL,
        status=200,
        json={},  # Not used
    )
    assert not contact.is_alert_sent
    send_webflow_contact_slack(contact.pk)
    assert len(responses.calls) == 1
    body_text = responses.calls[0].request.body.decode("utf-8")
    body_json = json.loads(body_text)
    assert str(contact.pk) in body_json["text"]
    contact = WebflowContact.objects.get(pk=contact.id)
    assert contact.is_alert_sent
