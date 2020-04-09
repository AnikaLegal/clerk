import json
from unittest import mock

import pytest
import responses
from django.conf import settings

from questions.services.slack import send_submission_slack
from questions.tests.factories import SubmissionFactory


@pytest.mark.django_db
@responses.activate
def test_slack_webhook():
    """
    Ensure we call Slack without anything exploding
    https://github.com/getsentry/responses
    """
    sub = SubmissionFactory()
    responses.add(
        method=responses.POST,
        url=settings.SUBMIT_SLACK_WEBHOOK_URL,
        status=200,
        json={},  # Not used
    )
    send_submission_slack(sub.pk)
    assert len(responses.calls) == 1
    body_text = responses.calls[0].request.body.decode("utf-8")
    body_json = json.loads(body_text)
    assert sub.topic in body_json["text"]
    assert str(sub.pk) in body_json["text"]
