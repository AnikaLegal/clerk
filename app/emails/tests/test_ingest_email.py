import json
import uuid

import pytest
from core.factories import EmailFactory, IssueFactory
from core.models.issue import CaseStage, Issue
from emails.models import EmailState
from emails.service import ingest_email_task

SUCCESS_TEST_CASES = [
    # Single recipient.
    {
        "received_data": {
            "from": "Example From <from@example.com>",
            "to": "case.0e62ccc2@mail.fake.anikalegal.org.au",
            "subject": "Hello World 1",
            "text": "Mrs. Elton began to think she had been wrong in disclaiming so warmly.",
            "envelope": '{"to":["case.0e62ccc2@mail.fake.anikalegal.org.au"],"from":"from@example.com"}',
        },
        "expected_parsed": {
            "from_address": "from@example.com",
            "to_address": "case.0e62ccc2@mail.fake.anikalegal.org.au",
            "cc_addresses": [],
            "subject": "Hello World 1",
            "text": "Mrs. Elton began to think she had been wrong in disclaiming so warmly.",
        },
    },
    # Multiple recipients and cc addresses.
    {
        "received_data": {
            "from": "From Example <from@example.com>",
            "to": "case.0e62ccc2@mail.fake.anikalegal.org.au, Example To <to@example.com>",
            "cc": "CC1 <cc_1@example.com>",
            "subject": "Hello World 2",
            "text": "Elinor's heart, which had undergone many changes in the course of this",
            "envelope": '{"to":["case.0e62ccc2@mail.fake.anikalegal.org.au"],"from":"from@example.com"}',
        },
        "expected_parsed": {
            "from_address": "from@example.com",
            "to_address": "case.0e62ccc2@mail.fake.anikalegal.org.au",
            "cc_addresses": ["cc_1@example.com", "to@example.com"],
            "subject": "Hello World 2",
            "text": "Elinor's heart, which had undergone many changes in the course of this",
        },
    },
    # Multiple recipients and cc addresses, different ordering of addresses.
    {
        "received_data": {
            "from": "Example From <from@example.com>",
            "to": "To Example <to@example.com>, case.0e62ccc2@mail.fake.anikalegal.org.au",
            "cc": "CC1 <cc_1@example.com>",
            "subject": "Hello World 3",
            "text": "Miss Bennet's astonishment was soon lessened by the strong sisterly",
            "envelope": '{"to":["case.0e62ccc2@mail.fake.anikalegal.org.au"],"from":"from@example.com"}',
        },
        "expected_parsed": {
            "from_address": "from@example.com",
            "to_address": "case.0e62ccc2@mail.fake.anikalegal.org.au",
            "cc_addresses": ["cc_1@example.com", "to@example.com"],
            "subject": "Hello World 3",
            "text": "Miss Bennet's astonishment was soon lessened by the strong sisterly",
        },
    },
    # Legacy domain recipients are still accepted.
    {
        "received_data": {
            "from": "Example From <from@example.com>",
            "to": "case.0e62ccc2@mail.legacy.fake.anikalegal.org.au, Example To <to@example.com>",
            "cc": "Example To <to@example.com>",
            "subject": "Hello World 5",
            "text": "She had been forced into prudence in her youth, she learned romance as she grew older.",
            "envelope": '{"to":["case.0e62ccc2@mail.legacy.fake.anikalegal.org.au","outside@example.com"],"from":"from@example.com"}',
        },
        "expected_parsed": {
            "from_address": "from@example.com",
            "to_address": "case.0e62ccc2@mail.fake.anikalegal.org.au",
            "cc_addresses": ["to@example.com"],
            "subject": "Hello World 5",
            "text": "She had been forced into prudence in her youth, she learned romance as she grew older.",
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
    settings.EMAIL_DOMAIN = "mail.fake.anikalegal.org.au"
    settings.EMAIL_DOMAIN_LEGACY = "mail.legacy.fake.anikalegal.org.au"
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
    assert email.cc_addresses == expected_parsed["cc_addresses"], email.to_address
    assert email.subject == expected_parsed["subject"]
    assert email.text == expected_parsed["text"]


SUCCESS_TEST_CASES_MULTIPLE_LOCAL_RECIPIENTS = [
    # Multiple local "to" addresses, multiple issues. The non-closed issue should be selected.
    {
        "issues": [
            {
                "id": uuid.UUID("0e62ccc2-b9ee-4a07-979a-da8a9d450404"),
                "stage": CaseStage.CLOSED,
                "created_at": "2024-01-01T00:00:00Z",
            },
            {
                "id": uuid.UUID("dccbca2b-ec3d-478a-8dfe-bf31ef99b11d"),
                "stage": CaseStage.UNSTARTED,
                "created_at": "2024-01-01T00:00:00Z",
            },
        ],
        "expected_issue_id": uuid.UUID("dccbca2b-ec3d-478a-8dfe-bf31ef99b11d"),
    },
    # Multiple local "to" addresses, multiple issues. The most recently created issue should be selected even if all issues are closed.
    {
        "issues": [
            {
                "id": uuid.UUID("0e62ccc2-b9ee-4a07-979a-da8a9d450404"),
                "stage": CaseStage.CLOSED,
                "created_at": "2024-01-01T00:00:00Z",
            },
            {
                "id": uuid.UUID("dccbca2b-ec3d-478a-8dfe-bf31ef99b11d"),
                "stage": CaseStage.CLOSED,
                "created_at": "2024-01-01T00:00:01Z",
            },
        ],
        "expected_issue_id": uuid.UUID("dccbca2b-ec3d-478a-8dfe-bf31ef99b11d"),
    },
]


@pytest.mark.django_db
@pytest.mark.parametrize("test_data", SUCCESS_TEST_CASES_MULTIPLE_LOCAL_RECIPIENTS)
def test_ingest_email__with_multiple_local_recipients(settings, test_data):
    settings.EMAIL_DOMAIN = "mail.fake.anikalegal.org.au"

    issues, expected_issue_id = (
        test_data["issues"],
        test_data["expected_issue_id"],
    )

    for issue_data in issues:
        IssueFactory(
            id=issue_data["id"],
            stage=issue_data["stage"],
            created_at=issue_data["created_at"],
        )

    # Get set of id prefixes for test data issues
    issue_prefixes = set(str(issue_data["id"]).split("-")[0] for issue_data in issues)
    received_data = {
        "from": "Example From <from@example.com>",
        "to": ", ".join(
            f"case.{prefix}@mail.fake.anikalegal.org.au" for prefix in issue_prefixes
        ),
        "subject": "Hello World 1",
        "text": "Mrs. Elton began to think she had been wrong in disclaiming so warmly.",
        "envelope": json.dumps(
            {
                "to": [
                    f"case.{prefix}@mail.fake.anikalegal.org.au"
                    for prefix in issue_prefixes
                ],
                "from": "from@example.com",
            }
        ),
    }

    email = EmailFactory(
        state=EmailState.RECEIVED, received_data=received_data, issue=None
    )
    ingest_email_task(email.pk)
    email.refresh_from_db()

    assert email.state == EmailState.INGESTED
    assert email.issue == Issue.objects.get(pk=expected_issue_id)
