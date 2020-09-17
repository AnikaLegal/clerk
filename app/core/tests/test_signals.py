from unittest import mock

import pytest

from questions.tests.factories import SubmissionFactory
from questions.services.slack import send_submission_slack
from questions.services.submission import send_submission_email


@pytest.mark.django_db
@pytest.mark.enable_signals
@mock.patch("questions.signals.submission.async_task", autospec=True)
def test_slack_and_email_sent_when_complete(mock_async):
    submission = SubmissionFactory()
    assert not submission.complete
    mock_async.assert_not_called()
    # Save the submission
    submission.complete = True
    submission.save()
    # Ensure tasks were dispatched
    mock_async.assert_has_calls(
        [
            mock.call(send_submission_slack, str(submission.pk)),
            mock.call(send_submission_email, str(submission.pk)),
        ]
    )


@pytest.mark.django_db
@pytest.mark.enable_signals
@mock.patch("questions.signals.submission.async_task", autospec=True)
def test_email_not_sent_when_already_sent(mock_async):
    submission = SubmissionFactory(is_alert_sent=True)
    assert not submission.complete
    mock_async.assert_not_called()
    # Save the submission
    submission.complete = True
    submission.save()
    # Ensure only email task was dispatched
    mock_async.assert_has_calls([mock.call(send_submission_email, str(submission.pk))])


@pytest.mark.django_db
@pytest.mark.enable_signals
@mock.patch("questions.signals.submission.async_task", autospec=True)
def test_email_not_sent_when_already_sent(mock_async):
    submission = SubmissionFactory(is_data_sent=True)
    assert not submission.complete
    mock_async.assert_not_called()
    # Save the submission
    submission.complete = True
    submission.save()
    # Ensure only alert task was dispatched
    mock_async.assert_has_calls([mock.call(send_submission_slack, str(submission.pk))])


@pytest.mark.django_db
@pytest.mark.enable_signals
@mock.patch("questions.signals.submission.async_task", autospec=True)
def test_email_not_sent_when_already_sent(mock_async):
    submission = SubmissionFactory(is_data_sent=True)
    assert not submission.complete
    mock_async.assert_not_called()
    # Save the submission
    submission.complete = True
    submission.save()
    # Ensure only alert task was dispatched
    mock_async.assert_has_calls([mock.call(send_submission_slack, str(submission.pk))])


@pytest.mark.django_db
@pytest.mark.enable_signals
@mock.patch("questions.signals.submission.async_task", autospec=True)
def test_nothing_sent_when_not_complete(mock_async):
    submission = SubmissionFactory()
    assert not submission.complete
    mock_async.assert_not_called()
    submission.save()
    # Ensure nothing was sent
    mock_async.assert_not_called()
