import pytest

from emails.service import parse_clerk_address, build_clerk_address
from emails.models import EmailState
from core.factories import EmailFactory, IssueFactory, UserFactory


@pytest.mark.django_db
def test_parse_email_address():
    issue_pk = "0e62ccc2-b9ee-4a07-979a-da8a9d450404"
    issue = IssueFactory(pk=issue_pk)
    sent_email = EmailFactory(
        to_addr="mattdsegal@gmail.com",
        to_addrs="mattdsegal@gmail.com",
        state=EmailState.SENT,
        issue=issue,
        sender=None,
    )
    issue_addr = build_clerk_address(sent_email)
    assert issue_addr == "case.0e62ccc2@fake.anikalegal.com"
    to_addrs = f"{issue_addr},  Matt Segal <matt@anikalegal.com>"
    received_email = EmailFactory(to_addrs=to_addrs, issue=None, sender=None)
    import pdb

    pdb.set_trace()
