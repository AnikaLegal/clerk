from unittest import mock

import pytest

from questions.tests.factories import SubmissionFactory


@pytest.mark.django_db
@pytest.mark.enable_signals
@mock.patch("questions.signals.submission.send_submission_email", autospec=True)
def test_email_sent_when_complete(mock_send):
    submission = SubmissionFactory()
    assert not submission.complete
    mock_send.assert_not_called()
    submission.complete = True
    submission.save()
    mock_send.assert_called_with(submission)


@pytest.mark.django_db
@pytest.mark.enable_signals
@mock.patch("questions.signals.submission.send_submission_email", autospec=True)
def test_email_not_sent_when_not_complete(mock_send):
    submission = SubmissionFactory()
    assert not submission.complete
    mock_send.assert_not_called()
    submission.save()
    mock_send.assert_not_called()
