from unittest import mock

import pytest

from core.factories import SubmissionFactory
from core.services.slack import send_submission_slack
from actionstep.services.actionstep import send_submission_actionstep


@pytest.mark.django_db
@pytest.mark.enable_signals
@mock.patch("core.signals.submission.async_task", autospec=True)
def test_all_tasks_dispatched_when_complete(mock_async):
    """
    Ensure all tasks are triggered when a new submission is first completed.
    """
    submission = SubmissionFactory()
    assert not submission.complete
    mock_async.assert_not_called()
    # Save the submission
    submission.complete = True
    submission.save()
    # Ensure tasks were dispatched
    mock_async.assert_has_calls(
        [mock.call(send_submission_slack, str(submission.pk))],
        [mock.call(send_submission_actionstep, str(submission.pk))],
    )


@pytest.mark.django_db
@pytest.mark.enable_signals
@mock.patch("core.signals.submission.async_task", autospec=True)
def test_slack_not_dispatched_when_already_sent(mock_async):
    """
    Ensure Slack message not sent twice.
    """
    submission = SubmissionFactory(is_alert_sent=True)
    assert not submission.complete
    mock_async.assert_not_called()
    # Save the submission
    submission.complete = True
    submission.save()
    # Ensure only email task was dispatched
    mock_async.assert_has_calls(
        [[mock.call(send_submission_actionstep, str(submission.pk))],]
    )


@pytest.mark.django_db
@pytest.mark.enable_signals
@mock.patch("core.signals.submission.async_task", autospec=True)
def test_actionstep_not_dispatched_when_already_sent(mock_async):
    """
    Ensure Actionstep integration not sent twice.
    """
    submission = SubmissionFactory(is_case_sent=True)
    assert not submission.complete
    mock_async.assert_not_called()
    # Save the submission
    submission.complete = True
    submission.save()
    # Ensure only email task was dispatched
    mock_async.assert_has_calls(
        [[mock.call(send_submission_slack, str(submission.pk))],]
    )


@pytest.mark.django_db
@pytest.mark.enable_signals
@mock.patch("core.signals.submission.async_task", autospec=True)
def test_nothing_sent_when_not_complete(mock_async):
    """
    Ensure nothing happens when submission is not completed but is saved.
    """
    submission = SubmissionFactory()
    assert not submission.complete
    mock_async.assert_not_called()
    submission.save()
    # Ensure nothing was sent
    mock_async.assert_not_called()
