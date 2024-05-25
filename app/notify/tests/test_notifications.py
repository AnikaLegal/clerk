from unittest.mock import patch, call

import pytest

from core.factories import IssueFactory, NotificationFactory, UserFactory
from notify.signals import get_notification_message_text

TEST_SLACK_USER_ID = "some-slack-id"


def mock_get_slack_user_by_email(email: str):
    return {"id": f"slack-{email}"}


@pytest.mark.enable_signals
@pytest.mark.django_db
@patch("notify.signals.get_slack_user_by_email", mock_get_slack_user_by_email)
@patch("notify.signals.send_slack_direct_message")
def test_send_notification__with_same_issue_topic(mock_send_message):
    paralegal = UserFactory()
    issue = IssueFactory(topic="REPAIRS", stage="UNSTARTED", paralegal=paralegal)
    notification = NotificationFactory(
        topic="REPAIRS",
        channel="SLACK",
        event="STAGE_CHANGE",
        event_stage="CLIENT_AGREEMENT",
        target="PARALEGAL",
    )

    assert mock_send_message.call_count == 0
    issue.stage = "CLIENT_AGREEMENT"
    issue.save()
    assert mock_send_message.call_count == 1
    mock_send_message.assert_has_calls(
        [
            call(
                get_notification_message_text(issue, notification),
                f"slack-{paralegal.email}",
            )
        ]
    )


@pytest.mark.enable_signals
@pytest.mark.django_db
@patch("notify.signals.get_slack_user_by_email", mock_get_slack_user_by_email)
@patch("notify.signals.send_slack_direct_message")
def test_send_notification__with_different_issue_topic(mock_send_message):
    issue = IssueFactory(topic="BONDS", stage="UNSTARTED", paralegal=UserFactory())
    NotificationFactory(
        topic="REPAIRS",
        channel="SLACK",
        event="STAGE_CHANGE",
        event_stage="CLIENT_AGREEMENT",
        target="PARALEGAL",
    )

    assert mock_send_message.call_count == 0
    issue.stage = "CLIENT_AGREEMENT"
    issue.save()
    assert mock_send_message.call_count == 0


@pytest.mark.enable_signals
@pytest.mark.django_db
@patch("notify.signals.get_slack_user_by_email", mock_get_slack_user_by_email)
@patch("notify.signals.send_slack_direct_message")
def test_send_notification__with_general_issue_topic(mock_send_message):
    paralegal = UserFactory()
    issue = IssueFactory(topic="BONDS", stage="UNSTARTED", paralegal=paralegal)
    notification = NotificationFactory(
        topic="GENERAL",
        channel="SLACK",
        event="STAGE_CHANGE",
        event_stage="CLIENT_AGREEMENT",
        target="PARALEGAL",
    )

    assert mock_send_message.call_count == 0
    issue.stage = "CLIENT_AGREEMENT"
    issue.save()
    assert mock_send_message.call_count == 1
    mock_send_message.assert_has_calls(
        [
            call(
                get_notification_message_text(issue, notification),
                f"slack-{paralegal.email}",
            )
        ]
    )


@pytest.mark.enable_signals
@pytest.mark.django_db
@patch("notify.signals.get_slack_user_by_email", mock_get_slack_user_by_email)
@patch("notify.signals.send_slack_direct_message")
def test_send_notification__with_lawyer_target(mock_send_message):
    lawyer = UserFactory()
    issue = IssueFactory(topic="BONDS", stage="UNSTARTED", lawyer=lawyer)
    notification = NotificationFactory(
        topic="GENERAL",
        channel="SLACK",
        event="STAGE_CHANGE",
        event_stage="CLIENT_AGREEMENT",
        target="LAWYER",
    )

    assert mock_send_message.call_count == 0
    issue.stage = "CLIENT_AGREEMENT"
    issue.save()
    assert mock_send_message.call_count == 1
    mock_send_message.assert_has_calls(
        [
            call(
                get_notification_message_text(issue, notification),
                f"slack-{lawyer.email}",
            )
        ]
    )
