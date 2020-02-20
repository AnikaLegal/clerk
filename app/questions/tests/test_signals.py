from unittest import mock

import pytest

from questions.tests.factories import SubmissionFactory


@pytest.mark.django_db
@pytest.mark.enable_signals
@mock.patch("questions.signals.submission.send_submission_slack", autospec=True)
@mock.patch("questions.signals.submission.send_submission_email", autospec=True)
@mock.patch("questions.signals.submission.async_task", autospec=True)
def test_email_sent_when_complete(mock_async, mock_send, mock_slack):
    submission = SubmissionFactory()
    assert not submission.complete
    mock_send.assert_not_called()
    mock_async.assert_not_called()
    mock_slack.assert_not_called()

    submission.complete = True
    submission.save()

    mock_async.assert_has_calls(
        [
            mock.call(mock_send, str(submission.pk)),
            mock.call(mock_slack, str(submission.pk)),
        ]
    )
    mock_send.assert_not_called()
    mock_slack.assert_not_called()


@pytest.mark.django_db
@pytest.mark.enable_signals
@mock.patch("questions.signals.submission.send_submission_email", autospec=True)
def test_email_not_sent_when_not_complete(mock_send):
    submission = SubmissionFactory()
    assert not submission.complete
    mock_send.assert_not_called()
    submission.save()
    mock_send.assert_not_called()
