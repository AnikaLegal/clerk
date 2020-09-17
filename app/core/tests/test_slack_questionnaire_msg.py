from unittest import mock

import pytest

from questions.services import slack
from questions.services.slack import send_submission_slack
from questions.tests.factories import SubmissionFactory
from questions.models import Submission


@pytest.mark.django_db
def test_slack_questionnaire_msg(monkeypatch):
    """
    Ensure we call Slack without anything exploding
    """
    mock_send_msg = mock.Mock()
    monkeypatch.setattr(slack, "send_slack_message", mock_send_msg)
    sub = SubmissionFactory()
    assert not sub.is_alert_sent
    mock_send_msg.assert_not_called()
    send_submission_slack(sub.pk)
    assert mock_send_msg.call_count == 1
    sub = Submission.objects.get(pk=sub.id)
    assert sub.is_alert_sent
