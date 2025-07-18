from unittest import mock

import pytest

from core.factories import IssueFactory
from core.models import Issue
from core.services.slack import send_issue_slack


@pytest.mark.django_db
@mock.patch("core.services.slack.send_slack_message", autospec=True)
def test_slack_issue_message(mock_send_slack_message: mock.Mock):
    """
    Ensure we call Slack without anything exploding
    """

    issue = IssueFactory(is_alert_sent=False)

    assert not issue.is_alert_sent
    mock_send_slack_message.assert_not_called()

    send_issue_slack(issue.pk)

    assert mock_send_slack_message.call_count == 1
    assert Issue.objects.get(pk=issue.id).is_alert_sent
