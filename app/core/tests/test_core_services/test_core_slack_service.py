from unittest import mock

import pytest

from core.services import slack
from core.services.slack import send_issue_slack
from core.factories import IssueFactory
from core.models import Issue


@pytest.mark.django_db
def test_slack_issuemission_message(monkeypatch):
    """
    Ensure we call Slack without anything exploding
    """
    mock_send_msg = mock.Mock()
    monkeypatch.setattr(slack, "send_slack_message", mock_send_msg)
    issue = IssueFactory()
    assert not issue.is_alert_sent
    mock_send_msg.assert_not_called()
    send_issue_slack(issue.pk)
    assert mock_send_msg.call_count == 1
    issue = Issue.objects.get(pk=issue.id)
    assert issue.is_alert_sent
