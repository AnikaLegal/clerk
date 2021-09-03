import pytest

from emails.service.send import build_clerk_address

from core.factories import IssueFactory


@pytest.mark.django_db
def test_build_email_address(settings):
    settings.EMAIL_DOMAIN = "fake.anikalegal.com"
    issue_pk = "0e62ccc2-b9ee-4a07-979a-da8a9d450404"
    issue = IssueFactory(id=issue_pk)
    issue_addr = build_clerk_address(issue)
    expected = "Anika Legal <case.0e62ccc2@fake.anikalegal.com>"
    assert issue_addr == expected
