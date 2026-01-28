import uuid

import pytest
from core.factories import EmailFactory, IssueFactory
from emails.models import EmailState
from emails.service import ingest_email_task

SUCCESS_TEST_CASES = [
    # Single recipient.
    {
        "received_data": {
            "from": "Example From <from@example.com>",
            "to": "case.0e62ccc2@fake.anikalegal.com",
            "subject": "Hello World 1",
            "text": "Mrs. Elton began to think she had been wrong in disclaiming so warmly.",
            "envelope": '{"to":["case.0e62ccc2@fake.anikalegal.com"],"from":"from@example.com"}',
        },
        "expected_parsed": {
            "from_address": "from@example.com",
            "to_address": "case.0e62ccc2@fake.anikalegal.com",
            "cc_addresses": [],
            "subject": "Hello World 1",
            "text": "Mrs. Elton began to think she had been wrong in disclaiming so warmly.",
        },
    },
    # Multiple recipients and cc addresses.
    {
        "received_data": {
            "from": "From Example <from@example.com>",
            "to": "case.0e62ccc2@fake.anikalegal.com, Example To <to@example.com>",
            "cc": "CC1 <cc_1@example.com>",
            "subject": "Hello World 2",
            "text": "Elinor’s heart, which had undergone many changes in the course of this",
            "envelope": '{"to":["case.0e62ccc2@fake.anikalegal.com"],"from":"from@example.com"}',
        },
        "expected_parsed": {
            "from_address": "from@example.com",
            "to_address": "case.0e62ccc2@fake.anikalegal.com",
            "cc_addresses": ["cc_1@example.com", "to@example.com"],
            "subject": "Hello World 2",
            "text": "Elinor’s heart, which had undergone many changes in the course of this",
        },
    },
    # Multiple recipients and cc addresses, different ordering of addresses.
    {
        "received_data": {
            "from": "Example From <from@example.com>",
            "to": "To Example <to@example.com>, case.0e62ccc2@fake.anikalegal.com",
            "cc": "CC1 <cc_1@example.com>",
            "subject": "Hello World 3",
            "text": "Miss Bennet’s astonishment was soon lessened by the strong sisterly",
            "envelope": '{"to":["case.0e62ccc2@fake.anikalegal.com"],"from":"from@example.com"}',
        },
        "expected_parsed": {
            "from_address": "from@example.com",
            "to_address": "case.0e62ccc2@fake.anikalegal.com",
            "cc_addresses": ["cc_1@example.com", "to@example.com"],
            "subject": "Hello World 3",
            "text": "Miss Bennet’s astonishment was soon lessened by the strong sisterly",
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
    issue = IssueFactory(id=uuid.UUID("0e62ccc2-b9ee-4a07-979a-da8a9d450404"))
    email = EmailFactory(
        state=EmailState.RECEIVED, received_data=received_data, issue=None
    )
    ingest_email_task(email.pk)
    email.refresh_from_db()

    assert email.state == EmailState.INGESTED
    assert email.issue == issue
    assert email.from_address == expected_parsed["from_address"]
    assert email.to_address == expected_parsed["to_address"]
    assert email.cc_addresses == expected_parsed["cc_addresses"]
    assert email.subject == expected_parsed["subject"]
    assert email.text == expected_parsed["text"]
