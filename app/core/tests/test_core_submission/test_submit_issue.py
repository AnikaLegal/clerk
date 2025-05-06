import pytest

from core.factories import FileUploadFactory, ClientFactory, TenancyFactory
from core.models import FileUpload, Issue, Submission
from core.models.upload import FileUpload
from core.services.submission import process_issue

"""
Test case #1
- Repairs
- no agent
- speaks Chinese as 1st language
- partner helps with rent
"""
REPAIRS_ANSWERS = {
    "ISSUES": "REPAIRS",
    "WEEKLY_HOUSEHOLD_INCOME": 1000,
    "WEEKLY_RENT": 500,
    "WORK_OR_STUDY_CIRCUMSTANCES": ["STUDENT", "WORKING_PART_TIME", "PARENT"],
    "LEGAL_CENTER_REFERRER": "Justice Connect",
    "REFERRER_TYPE": "LEGAL_CENTRE",
    "REPAIRS_REQUIRED": ["Water", "Roof"],
    "REPAIRS_ISSUE_DESCRIPTION": "Water pipe burst, damaging roof.",
    "REPAIRS_ISSUE_START": "2020-01-01",
    "REPAIRS_ISSUE_PHOTO": [
        {
            "id": "e249c2c2-15ed-4609-865f-c2109f06f6f8",
            "file": "https://example.com/e249c2c2-15ed-4609-865f-c2109f06f6f8.png",
            "issue": None,
        }
    ],
}
REPAIRS_ISSUE = {
    "client": "Matthew",
    "topic": "REPAIRS",
    "stage": None,
    "outcome": None,
    "outcome_notes": "",
    "provided_legal_services": False,
    "weekly_income": 1000,
    "weekly_rent": 500,
    "employment_status": ["STUDENT", "WORKING_PART_TIME", "PARENT"],
    "referrer_type": "LEGAL_CENTRE",
    "referrer": "Justice Connect",
    "answers": {
        "REPAIRS_REQUIRED": ["Water", "Roof"],
        "REPAIRS_ISSUE_DESCRIPTION": "Water pipe burst, damaging roof.",
        "REPAIRS_ISSUE_START": "2020-01-01",
    },
}
REPAIRS_UPLOADS = ["e249c2c2-15ed-4609-865f-c2109f06f6f8"]

"""
Test case #2
- Evictions
- Has agent
- Speaks English as 1st language
- Partner doesn't help with rent (is dependent)
"""
EVICTIONS_ANSWERS = {
    "ISSUES": "EVICTION",
    "WEEKLY_HOUSEHOLD_INCOME": 2000,
    "WEEKLY_RENT": 500,
    "WORK_OR_STUDY_CIRCUMSTANCES": ["WORKING_FULL_TIME"],
    "REFERRER_TYPE": "WORD_OF_MOUTH",
    "EVICTIONS_IS_UNPAID_RENT": True,
    "EVICTIONS_IS_ALREADY_REMOVED": False,
    "EVICTIONS_HAS_NOTICE": True,
    "EVICTIONS_DOCUMENTS_PROVIDED": [
        "Notice to Vacate",
        "Application for a Possession Order",
    ],
    "EVICTIONS_DOCUMENTS_UPLOAD": [
        {
            "id": "55bf8c07-5240-4253-9880-58c24f6afd8f",
            "file": "https://example.com/55bf8c07-5240-4253-9880-58c24f6afd8f.pdf",
        },
        {
            "id": "ab365dc1-5aae-4c5e-8528-a5fe08f57d35",
            "file": "https://example.com/ab365dc1-5aae-4c5e-8528-a5fe08f57d35.pdf",
        },
    ],
    "EVICTIONS_NOTICE_SEND_DATE": "1990-02-01",
    "EVICTIONS_NOTICE_VACATE_DATE": "2022-01-01",
    "EVICTIONS_DOC_DELIVERY_METHOD_NOTICE_TO_VACATE": "By registered post",
    "EVICTIONS_DOC_DELIVERY_TIME_NOTICE_TO_VACATE": "2000-12-31",
    "EVICTIONS_DOC_DELIVERY_METHOD_POSSESION_ORDER": "Another delivery method",
    "EVICTIONS_DOC_DELIVERY_TIME_POSSESION_ORDER": "2020-03-01",
    "EVICTIONS_IS_VCAT_DATE": True,
    "EVICTIONS_VCAT_DATE": "2022-02-01",
    "EVICTIONS_RENT_UNPAID": 11000,
    "EVICTIONS_RENT_CYCLE": "FORTNIGHTLY",
    "EVICTIONS_IS_ON_PAYMENT_PLAN": False,
    "EVICTIONS_CAN_AFFORD_PAYMENT_PLAN": "YES",
    "EVICTIONS_PAYMENT_AMOUNT": 200,
    "EVICTIONS_PAYMENT_FAIL_REASON": [
        "Unable to work",
        "Another tenant moving out",
    ],
    "EVICTIONS_PAYMENT_FAIL_DESCRIPTION": "Got fired and friend moving in with parents",
    "EVICTIONS_PAYMENT_FAIL_CHANGE": "Got a new job",
    "EVICTIONS_MISC": "Landlord harasses me with phone calls",
}
EVICTIONS_ISSUE = {
    "client": "Matthew",
    "topic": "EVICTION_ARREARS",
    "stage": None,
    "outcome": None,
    "outcome_notes": "",
    "provided_legal_services": False,
    "weekly_income": 2000,
    "weekly_rent": 500,
    "employment_status": ["WORKING_FULL_TIME"],
    "referrer_type": "WORD_OF_MOUTH",
    "referrer": "",
    "answers": {
        "EVICTIONS_IS_UNPAID_RENT": True,
        "EVICTIONS_IS_ALREADY_REMOVED": False,
        "EVICTIONS_HAS_NOTICE": True,
        "EVICTIONS_DOCUMENTS_PROVIDED": [
            "Notice to Vacate",
            "Application for a Possession Order",
        ],
        "EVICTIONS_NOTICE_SEND_DATE": "1990-02-01",
        "EVICTIONS_NOTICE_VACATE_DATE": "2022-01-01",
        "EVICTIONS_DOC_DELIVERY_METHOD_NOTICE_TO_VACATE": "By registered post",
        "EVICTIONS_DOC_DELIVERY_TIME_NOTICE_TO_VACATE": "2000-12-31",
        "EVICTIONS_DOC_DELIVERY_METHOD_POSSESION_ORDER": "Another delivery method",
        "EVICTIONS_DOC_DELIVERY_TIME_POSSESION_ORDER": "2020-03-01",
        "EVICTIONS_IS_VCAT_DATE": True,
        "EVICTIONS_VCAT_DATE": "2022-02-01",
        "EVICTIONS_RENT_UNPAID": 11000,
        "EVICTIONS_RENT_CYCLE": "FORTNIGHTLY",
        "EVICTIONS_IS_ON_PAYMENT_PLAN": False,
        "EVICTIONS_CAN_AFFORD_PAYMENT_PLAN": "YES",
        "EVICTIONS_PAYMENT_AMOUNT": 200,
        "EVICTIONS_PAYMENT_FAIL_REASON": [
            "Unable to work",
            "Another tenant moving out",
        ],
        "EVICTIONS_PAYMENT_FAIL_DESCRIPTION": "Got fired and friend moving in with parents",
        "EVICTIONS_PAYMENT_FAIL_CHANGE": "Got a new job",
        "EVICTIONS_MISC": "Landlord harasses me with phone calls",
    },
}
EVICTIONS_UPLOADS = [
    "55bf8c07-5240-4253-9880-58c24f6afd8f",
    "ab365dc1-5aae-4c5e-8528-a5fe08f57d35",
]


"""
Test case #3
- Bonds
- Mostly same as repairs
"""
BONDS_ANSWERS = {
    "ISSUES": "BONDS",
    "WEEKLY_HOUSEHOLD_INCOME": 1337,
    "WEEKLY_RENT": None,
    "WORK_OR_STUDY_CIRCUMSTANCES": ["LOOKING_FOR_WORK", "STUDENT"],
    "COMMUNITY_ORGANISATION_REFERRER": "Jewish Care",
    "REFERRER_TYPE": "COMMUNITY_ORGANISATION",
    "BONDS_CLAIM_REASONS": [
        "Damage",
        "Rent or other money owing",
        "Cleaning",
        "Locks and security devices",
        "Other reason",
    ],
    "BONDS_MOVE_OUT_DATE": "1990-01-01",
    "BONDS_LOCKS_CLAIM_AMOUNT": 123,
    "BONDS_DAMAGE_CLAIM_AMOUNT": 234,
    "BONDS_OTHER_REASONS_AMOUNT": 345,
    "BONDS_CLEANING_CLAIM_AMOUNT": 456,
    "BONDS_MONEY_OWED_CLAIM_AMOUNT": 567,
    "BONDS_DAMAGE_CAUSED_BY_TENANT": True,
    "BONDS_LOCKS_CHANGED_BY_TENANT": True,
    "BONDS_MONEY_IS_OWED_BY_TENANT": True,
    "BONDS_OTHER_REASONS_DESCRIPTION": "bad breath",
    "BONDS_CLEANING_CLAIM_DESCRIPTION": "real dirty",
    "BONDS_MONEY_OWED_CLAIM_DESCRIPTION": "stole my car",
    "BONDS_DAMAGE_CLAIM_DESCRIPTION": "broke the toilet",
    "BONDS_LANDLORD_INTENTS_TO_MAKE_CLAIM": True,
    "BONDS_TENANT_HAS_RTBA_APPLICATION_COPY": True,
    "BONDS_HAS_LANDLORD_MADE_RTBA_APPLICATION": True,
    "BONDS_RTBA_APPLICATION_UPLOAD": [
        {
            "id": "24f87cdb-619c-4159-8264-d07c783d4712",
            "file": "https://example.com/file-uploads/ad3cab0a69bd1b07988130541d168011.pdf",
        }
    ],
    "BONDS_LOCKS_CHANGE_QUOTE": [
        {
            "id": "14f87cdb-619c-4159-8264-d07c783d4715",
            "file": "https://example.com/file-uploads/5d3cab0a69bd1b07988130541d168019.pdf",
        }
    ],
    "BONDS_DAMAGE_QUOTE_UPLOAD": [
        {
            "id": "12b25edb-e19d-4a90-a20f-fcfcae84f824",
            "file": "https://example.com/file-uploads/49e461abed6b9d81d450726f10f64cc6.png",
        }
    ],
    "BONDS_CLEANING_DOCUMENT_UPLOADS": [
        {
            "id": "6e51ef33-82a4-4bc5-8a32-e0f883b750fb",
            "file": "https://example.com/file-uploads/5d3cab0a69bd1b07988130541d168019.pdf",
        },
        {
            "id": "862532ab-e014-4434-9921-8e147fc5d230",
            "file": "https://example.com/file-uploads/67bdb73c57fa8e3b7f01703ddd34d76b.png",
        },
    ],
}
BONDS_ISSUE = {
    "client": "Matthew",
    "topic": "BONDS",
    "stage": None,
    "outcome": None,
    "outcome_notes": "",
    "provided_legal_services": False,
    "weekly_income": 1337,
    "weekly_rent": None,
    "employment_status": ["LOOKING_FOR_WORK", "STUDENT"],
    "referrer_type": "COMMUNITY_ORGANISATION",
    "referrer": "Jewish Care",
    "answers": {
        "BONDS_CLAIM_REASONS": [
            "Damage",
            "Rent or other money owing",
            "Cleaning",
            "Locks and security devices",
            "Other reason",
        ],
        "BONDS_MOVE_OUT_DATE": "1990-01-01",
        "BONDS_LOCKS_CLAIM_AMOUNT": 123,
        "BONDS_DAMAGE_CLAIM_AMOUNT": 234,
        "BONDS_OTHER_REASONS_AMOUNT": 345,
        "BONDS_CLEANING_CLAIM_AMOUNT": 456,
        "BONDS_MONEY_OWED_CLAIM_AMOUNT": 567,
        "BONDS_DAMAGE_CAUSED_BY_TENANT": True,
        "BONDS_LOCKS_CHANGED_BY_TENANT": True,
        "BONDS_MONEY_IS_OWED_BY_TENANT": True,
        "BONDS_OTHER_REASONS_DESCRIPTION": "bad breath",
        "BONDS_CLEANING_CLAIM_DESCRIPTION": "real dirty",
        "BONDS_MONEY_OWED_CLAIM_DESCRIPTION": "stole my car",
        "BONDS_DAMAGE_CLAIM_DESCRIPTION": "broke the toilet",
        "BONDS_LANDLORD_INTENTS_TO_MAKE_CLAIM": True,
        "BONDS_TENANT_HAS_RTBA_APPLICATION_COPY": True,
        "BONDS_HAS_LANDLORD_MADE_RTBA_APPLICATION": True,
    },
}
BONDS_UPLOADS = [
    "24f87cdb-619c-4159-8264-d07c783d4712",
    "14f87cdb-619c-4159-8264-d07c783d4715",
    "12b25edb-e19d-4a90-a20f-fcfcae84f824",
    "6e51ef33-82a4-4bc5-8a32-e0f883b750fb",
    "862532ab-e014-4434-9921-8e147fc5d230",
]


PROCESS_TESTS = (
    # answers, expected_client, expected_landlord, expected_agent, expected_tenancy, expected_issue
    (
        REPAIRS_ANSWERS,
        REPAIRS_ISSUE,
        REPAIRS_UPLOADS,
    ),
    (
        EVICTIONS_ANSWERS,
        EVICTIONS_ISSUE,
        EVICTIONS_UPLOADS,
    ),
    (
        BONDS_ANSWERS,
        BONDS_ISSUE,
        BONDS_UPLOADS,
    ),
)


@pytest.mark.django_db
@pytest.mark.parametrize(
    ",".join(
        [
            "answers",
            "expected_issue",
            "expected_uploads",
        ]
    ),
    PROCESS_TESTS,
)
def test_process_submission(
    answers,
    expected_issue,
    expected_uploads,
):
    """
    Ensure that intake form submissions can be processed,
    """
    client = ClientFactory(first_name="Matthew")
    tenancy = TenancyFactory()

    # Create some file uploads that we can associate with the issue.
    for upload_id in expected_uploads:
        FileUploadFactory(id=upload_id, issue=None)

    assert Issue.objects.count() == 0
    assert FileUpload.objects.count() == len(expected_uploads)

    sub = Submission.objects.create(answers=answers)
    process_issue(answers, client, tenancy)

    assert Issue.objects.count() == 1
    assert FileUpload.objects.count() == len(expected_uploads)

    issue = Issue.objects.last()
    for k, v in expected_issue.items():
        if k == "client":
            getattr(issue, k).first_name == v, k
    else:
        assert getattr(issue, k) == v, k

    for upload in FileUpload.objects.all():
        assert str(upload.id) in expected_uploads
        assert upload.issue == issue
