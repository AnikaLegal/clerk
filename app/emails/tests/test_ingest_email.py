import pytest

from emails.service import receive_email_task

from emails.models import EmailState
from core.factories import EmailFactory, IssueFactory

SUCCESS_TEST_CASES = [
    # Single recipient.
    {
        "expected_parsed": {
            "from_address": "mattdsegal@gmail.com",
            "to_address": "case.0e62ccc2@fake.anikalegal.com",
            "cc_addresses": [],
            "subject": "Hello World 1",
            "text": "Mrs. Elton began to think she had been wrong in disclaiming so warmly.",
        },
        "received_data": {
            "to": "case.0e62ccc2@fake.anikalegal.com",
            "from": "matthew segal <mattdsegal@gmail.com>",
            "text": "Mrs. Elton began to think she had been wrong in disclaiming so warmly.",
            "subject": "Hello World 1",
            "envelope": '{"to":["case.0e62ccc2@fake.anikalegal.com"],"from":"mattdsegal@gmail.com"}',
        },
    },
    # Multiple recipients and cc addresses.
    {
        "expected_parsed": {
            "from_address": "mattdsegal@gmail.com",
            "to_address": "case.0e62ccc2@fake.anikalegal.com",
            "cc_addresses": ["mattdsegal@gmail.com", "matt@anikalegal.com"],
            "subject": "Hello World 2",
            "text": "Elinor’s heart, which had undergone many changes in the course of this",
        },
        "received_data": {
            "cc": "Me <mattdsegal@gmail.com>",
            "to": "case.0e62ccc2@fake.anikalegal.com,  Matt Segal <matt@anikalegal.com>",
            "from": "matthew segal <mattdsegal@gmail.com>",
            "text": "Elinor’s heart, which had undergone many changes in the course of this",
            "subject": "Hello World 2",
            "envelope": '{"to":["case.0e62ccc2@fake.anikalegal.com"],"from":"mattdsegal@gmail.com"}',
        },
    },
    # Multiple recipients and cc addresses, different ordering of addresses.
    {
        "expected_parsed": {
            "from_address": "mattdsegal@gmail.com",
            "to_address": "case.0e62ccc2@fake.anikalegal.com",
            "cc_addresses": ["mattdsegal@gmail.com", "matt@anikalegal.com"],
            "subject": "Hello World 3",
            "text": "Miss Bennet’s astonishment was soon lessened by the strong sisterly",
        },
        "received_data": {
            "cc": "Me <mattdsegal@gmail.com>",
            "to": "Matt Segal <matt@anikalegal.com>, case.0e62ccc2@fake.anikalegal.com",
            "from": "matthew segal <mattdsegal@gmail.com>",
            "text": "Miss Bennet’s astonishment was soon lessened by the strong sisterly",
            "subject": "Hello World 3",
            "envelope": '{"to":["case.0e62ccc2@fake.anikalegal.com"],"from":"mattdsegal@gmail.com"}',
        },
    },
]


@pytest.mark.django_db
@pytest.mark.parametrize("test_data", SUCCESS_TEST_CASES)
def test_ingest_email__with_success(settings, test_data):
    expected_parsed, received_data = (
        test_data["expected_parsed"],
        test_data["received_data"],
    )
    settings.EMAIL_DOMAIN = "fake.anikalegal.com"
    issue_pk = "0e62ccc2-b9ee-4a07-979a-da8a9d450404"
    IssueFactory(id=issue_pk)
    email = EmailFactory(
        state=EmailState.RECEIVED, received_data=received_data, issue=None
    )
    receive_email_task(email.pk)
    email.refresh_from_db()
    assert email.state == EmailState.INGESTED
    assert str(email.issue_id) == issue_pk
    assert email.from_address == expected_parsed["from_address"]
    assert email.to_address == expected_parsed["to_address"]
    assert email.cc_addresses == expected_parsed["cc_addresses"]
    assert email.subject == expected_parsed["subject"]
    assert email.text == expected_parsed["text"]
