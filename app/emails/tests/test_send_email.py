from unittest.mock import patch
from urllib.error import URLError

import pytest
from python_http_client.exceptions import HTTPError

from emails.models import Email, EmailState
from emails.service.send import build_clerk_address, send_email_task

from core.factories import EmailFactory, IssueFactory


@pytest.mark.django_db
def test_build_email_address(settings):
    settings.EMAIL_DOMAIN = "mail.fake.anikalegal.org.au"
    issue_pk = "0e62ccc2-b9ee-4a07-979a-da8a9d450404"
    issue = IssueFactory(id=issue_pk)
    issue_addr = build_clerk_address(issue)
    expected = "Anika Legal <case.0e62ccc2@mail.fake.anikalegal.org.au>"
    assert issue_addr == expected


@pytest.mark.django_db
@pytest.mark.parametrize(
    "error",
    [
        # SendGrid returns a structured response (e.g. 413 for an oversized email).
        HTTPError(413, "Payload Too Large", b"too big", {}),
        # Or the load balancer severs the connection mid-upload, with no response.
        URLError("EOF occurred in violation of protocol"),
    ],
)
@patch("emails.service.send.send_email")
def test_send_email_task_marks_failure_on_sendgrid_error(mock_send_email, error):
    """A SendGrid rejection should flag the email as failed, not stay stuck."""
    mock_send_email.side_effect = error
    email = EmailFactory(state=EmailState.READY_TO_SEND)

    # @sentry_task swallows the re-raised error after capturing it, so the task
    # itself returns normally; what matters is the email is flagged as failed.
    send_email_task(email.pk)

    email.refresh_from_db()
    assert email.state == EmailState.DELIVERY_FAILURE
