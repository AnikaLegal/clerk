from unittest import mock

import pytest

from core.factories import IssueFactory
from core.models import Submission
from core.services.slack import send_issue_slack
from core.services.submission import process_submission


@pytest.mark.django_db
@pytest.mark.enable_signals
@mock.patch("core.signals.submission.async_task", autospec=True)
def test_submission_not_processed_on_save_if_not_complete(mock_async):
    mock_async.assert_not_called()
    sub = Submission.objects.create(answers={})
    assert not sub.is_complete
    # Ensure no tasks were dispatched
    mock_async.assert_not_called()


@pytest.mark.django_db
@pytest.mark.enable_signals
@mock.patch("core.signals.submission.async_task", autospec=True)
def test_submission_processed_on_save_if_complete(mock_async):
    mock_async.assert_not_called()
    sub = Submission.objects.create(answers={}, is_complete=True)
    assert sub.is_complete and not sub.is_processed
    # Ensure tasks were dispatched
    mock_async.assert_has_calls(
        [mock.call(process_submission, str(sub.pk))],
    )


@pytest.mark.django_db
@pytest.mark.enable_signals
@mock.patch("core.signals.submission.async_task", autospec=True)
def test_submission_not_processed_on_save_if_processed(mock_async):
    mock_async.assert_not_called()
    sub = Submission.objects.create(answers={}, is_complete=True, is_processed=True)
    assert sub.is_complete and sub.is_processed
    # Ensure no tasks were dispatched
    mock_async.assert_not_called()


@pytest.mark.django_db
@pytest.mark.enable_signals
@mock.patch("core.signals.issue.async_task", autospec=True)
def test_all_tasks_dispatched_when_complete(mock_async):
    """
    Ensure all tasks are triggered when a new issue is first completed.
    """
    mock_async.assert_not_called()
    issue = IssueFactory(is_alert_sent=False, is_case_sent=False)
    issue.save()
    # Ensure tasks were dispatched
    mock_async.assert_has_calls(
        [mock.call(send_issue_slack, str(issue.pk))],
    )


@pytest.mark.django_db
@pytest.mark.enable_signals
@mock.patch("core.signals.issue.async_task", autospec=True)
def test_slack_not_dispatched_when_already_sent(mock_async):
    """
    Ensure Slack message not sent twice.
    """
    mock_async.assert_not_called()
    issue = IssueFactory(is_alert_sent=False, is_case_sent=True)
    issue.save()
    # Ensure only email task was dispatched
    mock_async.assert_has_calls([mock.call(send_issue_slack, str(issue.pk))])
