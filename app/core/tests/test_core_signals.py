from unittest import mock

import pytest

from core.factories import IssueFactory
from core.services.slack import send_issue_slack
from actionstep.services.actionstep import send_issue_actionstep


@pytest.mark.django_db
@pytest.mark.enable_signals
@mock.patch("core.signals.issue.async_task", autospec=True)
def test_all_tasks_dispatched_when_complete(mock_async):
    """
    Ensure all tasks are triggered when a new issue is first completed.
    """
    issue = IssueFactory()
    assert not issue.is_submitted
    mock_async.assert_not_called()
    # Save the issue
    issue.is_submitted = True
    issue.save()
    # Ensure tasks were dispatched
    mock_async.assert_has_calls(
        [mock.call(send_issue_slack, str(issue.pk))],
        [mock.call(send_issue_actionstep, str(issue.pk))],
    )


@pytest.mark.django_db
@pytest.mark.enable_signals
@mock.patch("core.signals.issue.async_task", autospec=True)
def test_slack_not_dispatched_when_already_sent(mock_async):
    """
    Ensure Slack message not sent twice.
    """
    issue = IssueFactory(is_alert_sent=True)
    assert not issue.is_submitted
    mock_async.assert_not_called()
    # Save the issue
    issue.is_submitted = True
    issue.save()
    # Ensure only email task was dispatched
    mock_async.assert_has_calls([mock.call(send_issue_actionstep, str(issue.pk))])


@pytest.mark.django_db
@pytest.mark.enable_signals
@mock.patch("core.signals.issue.async_task", autospec=True)
def test_actionstep_not_dispatched_when_already_sent(mock_async):
    """
    Ensure Actionstep integration not sent twice.
    """
    issue = IssueFactory(is_case_sent=True)
    assert not issue.is_submitted
    mock_async.assert_not_called()
    # Save the issue
    issue.is_submitted = True
    issue.save()
    # Ensure only email task was dispatched
    mock_async.assert_has_calls([mock.call(send_issue_slack, str(issue.pk))])


@pytest.mark.django_db
@pytest.mark.enable_signals
@mock.patch("core.signals.issue.async_task", autospec=True)
def test_nothing_sent_when_not_complete(mock_async):
    """
    Ensure nothing happens when issue is not completed but is saved.
    """
    issue = IssueFactory()
    assert not issue.is_submitted
    mock_async.assert_not_called()
    issue.save()
    # Ensure nothing was sent
    mock_async.assert_not_called()
