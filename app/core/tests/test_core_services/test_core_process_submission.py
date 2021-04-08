from datetime import datetime

import pytest
from django.utils import timezone

from core.factories import FileUploadFactory
from core.models import Client, FileUpload, Issue, Person, Submission, Tenancy
from core.models.upload import FileUpload
from core.services.submission import process_submission

"""
Test case #1
- Repairs
- no agent
- speaks Chinese as 1st language
- partner helps with rent
"""
REPAIRS_ANSWERS = {
    "ADDRESS": "123 Fake St",
    "AVAILIBILITY": ["WEEK_DAY", "WEEK_EVENING"],
    "CAN_SPEAK_NON_ENGLISH": True,
    "DOB": "1990-08-15",
    "EMAIL": "mattdsegal@gmail.com",
    "FIRST_LANGUAGE": "Chinese",
    "FIRST_NAME": "Matthew",
    "GENDER": "male",
    "IS_ABORIGINAL_OR_TORRES_STRAIT_ISLANDER": False,
    "IS_MULTI_INCOME_HOUSEHOLD": True,
    "IS_ON_LEASE": "YES",
    "ISSUES": "REPAIRS",
    "LANDLORD_ADDRESS": "321 Fake St, Fitzroy 3065",
    "LANDLORD_EMAIL": "john.smith@landlord.com",
    "LANDLORD_NAME": "John Smith",
    "LANDLORD_PHONE": "0411111122",
    "LAST_NAME": "Segal",
    "LEGAL_ACCESS_DIFFICULTIES": ["SUBSTANCE_ABUSE", "DISABILITY"],
    "LEGAL_CENTER_REFERRER": "Justice Connect",
    "NUMBER_OF_DEPENDENTS": 0,
    "PHONE": "0431417373",
    "POSTCODE": 3065,
    "PROPERTY_MANAGER_IS_AGENT": False,
    "REFERRER_TYPE": "LEGAL_CENTRE",
    "SPECIAL_CIRCUMSTANCES": ["CENTRELINK", "PUBLIC_HOUSING"],
    "START_DATE": "2019-01-01",
    "SUBURB": "Fitzroy",
    "WEEKLY_INCOME_MULTI": 1000,
    "WEEKLY_RENT_MULTI": 668,
    "WORK_OR_STUDY_CIRCUMSTANCES": ["STUDENT", "WORKING_PART_TIME"],
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
    "RENTAL_CIRCUMSTANCES": "PARTNER",
}
REPAIRS_CLIENT = {
    "first_name": "Matthew",
    "last_name": "Segal",
    "gender": "male",
    "email": "mattdsegal@gmail.com",
    "date_of_birth": "1990-08-15",
    "phone_number": "0431417373",
    "call_times": ["WEEK_DAY", "WEEK_EVENING"],
    "employment_status": ["STUDENT", "WORKING_PART_TIME"],
    "special_circumstances": ["CENTRELINK", "PUBLIC_HOUSING"],
    "weekly_income": 1000,
    "weekly_rent": 668,
    "rental_circumstances": "PARTNER",
    "legal_access_difficulties": ["SUBSTANCE_ABUSE", "DISABILITY"],
    "is_multi_income_household": True,
    "number_of_dependents": 0,
    "primary_language_non_english": True,
    "primary_language": "Chinese",
    "is_aboriginal_or_torres_strait_islander": False,
    "referrer_type": "LEGAL_CENTRE",
    "referrer": "Justice Connect",
}
REPAIRS_LANDLORD = {
    "full_name": "John Smith",
    "email": "john.smith@landlord.com",
    "address": "321 Fake St, Fitzroy 3065",
    "phone_number": "0411111122",
}
REPAIRS_AGENT = None
REPAIRS_TENANCY = {
    "client": "Matthew",
    "address": "123 Fake St",
    "suburb": "Fitzroy",
    "postcode": "3065",
    "started": "2019-01-01",
    "is_on_lease": "YES",
    "landlord": "John Smith",
    "agent": None,
}
REPAIRS_ISSUE = {
    "client": "Matthew",
    "topic": "REPAIRS",
    "stage": None,
    "outcome": None,
    "outcome_notes": "",
    "provided_legal_services": False,
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
    "ADDRESS": "123 Fake St",
    "AGENT_ADDRESS": "321 Fake St",
    "AGENT_EMAIL": "sarah.smith@agent.com",
    "AGENT_NAME": "Sarah Smith",
    "AGENT_PHONE": "0411111188",
    "AVAILIBILITY": ["WEEK_DAY", "SUNDAY"],
    "CAN_SPEAK_NON_ENGLISH": False,
    "FIRST_LANGUAGE": None,
    "DOB": "1990-02-01",
    "EMAIL": "mattdsegal@gmail.com",
    "FIRST_NAME": "Matthew",
    "GENDER": "genderqueer",
    "IS_ABORIGINAL_OR_TORRES_STRAIT_ISLANDER": True,
    "IS_MULTI_INCOME_HOUSEHOLD": False,
    "IS_ON_LEASE": "YES",
    "ISSUES": "EVICTION",
    "LANDLORD_NAME": "John Smith",
    "LAST_NAME": "Segal",
    "NUMBER_OF_DEPENDENTS": 1,
    "PHONE": "0431417373",
    "POSTCODE": 3065,
    "PROPERTY_MANAGER_IS_AGENT": True,
    "REFERRER_TYPE": "WORD_OF_MOUTH",
    "RENTAL_CIRCUMSTANCES": "PARTNER",
    "START_DATE": "1999-01-01",
    "SUBURB": "Fitzroy",
    "WEEKLY_INCOME": 2000,
    "WEEKLY_RENT": 1100,
    "WORK_OR_STUDY_CIRCUMSTANCES": ["WORKING_FULL_TIME"],
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

EVICTIONS_CLIENT = {
    "first_name": "Matthew",
    "last_name": "Segal",
    "gender": "genderqueer",
    "email": "mattdsegal@gmail.com",
    "date_of_birth": "1990-02-01",
    "phone_number": "0431417373",
    "call_times": ["WEEK_DAY", "SUNDAY"],
    "employment_status": ["WORKING_FULL_TIME"],
    "special_circumstances": [],
    "weekly_income": 2000,
    "weekly_rent": 1100,
    "rental_circumstances": "PARTNER",
    "legal_access_difficulties": [],
    "is_multi_income_household": False,
    "number_of_dependents": 1,
    "primary_language_non_english": False,
    "primary_language": "",
    "is_aboriginal_or_torres_strait_islander": True,
    "referrer_type": "WORD_OF_MOUTH",
    "referrer": "",
}
EVICTIONS_LANDLORD = {
    "full_name": "John Smith",
    "email": "",
    "address": "",
    "phone_number": "",
}
EVICTIONS_AGENT = {
    "full_name": "Sarah Smith",
    "email": "sarah.smith@agent.com",
    "address": "321 Fake St",
    "phone_number": "0411111188",
}
EVICTIONS_TENANCY = {
    "client": "Matthew",
    "address": "123 Fake St",
    "suburb": "Fitzroy",
    "postcode": "3065",
    "started": "1999-01-01",
    "is_on_lease": "YES",
    "landlord": "John Smith",
    "agent": "Sarah Smith",
}
EVICTIONS_ISSUE = {
    "client": "Matthew",
    "topic": "EVICTION",
    "stage": None,
    "outcome": None,
    "outcome_notes": "",
    "provided_legal_services": False,
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
- Rent reduction
- Has no agent
- Speaks Russian as 1st language
- Partner doesn't help with rent (no dependents)
"""
RENT_REDUCTION_ANSWERS = {
    "ADDRESS": "123 Fake St",
    "AVAILIBILITY": ["SUNDAY"],
    "CAN_SPEAK_NON_ENGLISH": True,
    "CHARITY_REFERRER": "Jewish Care",
    "DOB": "1990-08-15",
    "EMAIL": "mattdsegal@gmail.com",
    "FIRST_LANGUAGE": "Russian",
    "FIRST_NAME": "Matthew",
    "GENDER": "omitted",
    "IS_ABORIGINAL_OR_TORRES_STRAIT_ISLANDER": False,
    "IS_MULTI_INCOME_HOUSEHOLD": False,
    "IS_ON_LEASE": "YES",
    "ISSUES": "RENT_REDUCTION",
    "LANDLORD_ADDRESS": "321 Fake St, Fitzroy 3065",
    "LANDLORD_EMAIL": "john.smith@landlord.com",
    "LANDLORD_NAME": "John Smith",
    "LANDLORD_PHONE": "0422211133",
    "LAST_NAME": "Segal",
    "NUMBER_OF_DEPENDENTS": 0,
    "PHONE": "0431417373",
    "POSTCODE": 3065,
    "PROPERTY_MANAGER_IS_AGENT": False,
    "REFERRER_TYPE": "CHARITY",
    "RENTAL_CIRCUMSTANCES": "SOLO",
    "SPECIAL_CIRCUMSTANCES": ["REFUGEE"],
    "START_DATE": "1990-01-01",
    "SUBURB": "Fitzroy",
    "WEEKLY_INCOME": 1337,
    "WEEKLY_RENT": 1336,
    "WORK_OR_STUDY_CIRCUMSTANCES": ["LOOKING_FOR_WORK", "STUDENT"],
    "RENT_REDUCTION_ISSUES": ["Another tenant moved out"],
    "RENT_REDUCTION_ISSUE_DESCRIPTION": "Another tenant moved out coz they lost their job and I cannot afford the rent",
    "RENT_REDUCTION_ISSUE_START": "2020-08-02",
    "RENT_REDUCTION_ISSUE_PHOTO": [
        {
            "id": "380aeaa4-c767-4a9b-90ad-b4d5b4e16859",
            "file": "https://example.com/380aeaa4-c767-4a9b-90ad-b4d5b4e16859.pdf",
        }
    ],
    "RENT_REDUCTION_IS_NOTICE_TO_VACATE": True,
    "RENT_REDUCTION_NOTICE_TO_VACATE_DOCUMENT": [
        {
            "id": "1f5f6874-9af3-4996-ab8c-022e3877f50f",
            "file": "https://example.com/1f5f6874-9af3-4996-ab8c-022e3877f50f.pdf",
        }
    ],
}

RENT_REDUCTION_CLIENT = {
    "first_name": "Matthew",
    "last_name": "Segal",
    "gender": "omitted",
    "email": "mattdsegal@gmail.com",
    "date_of_birth": "1990-08-15",
    "phone_number": "0431417373",
    "call_times": ["SUNDAY"],
    "employment_status": ["LOOKING_FOR_WORK", "STUDENT"],
    "special_circumstances": ["REFUGEE"],
    "weekly_income": 1337,
    "weekly_rent": 1336,
    "rental_circumstances": "SOLO",
    "legal_access_difficulties": [],
    "is_multi_income_household": False,
    "number_of_dependents": 0,
    "primary_language_non_english": True,
    "primary_language": "Russian",
    "is_aboriginal_or_torres_strait_islander": False,
    "referrer_type": "CHARITY",
    "referrer": "Jewish Care",
}
RENT_REDUCTION_LANDLORD = {
    "full_name": "John Smith",
    "email": "john.smith@landlord.com",
    "address": "321 Fake St, Fitzroy 3065",
    "phone_number": "0422211133",
}
RENT_REDUCTION_AGENT = None
RENT_REDUCTION_TENANCY = {
    "client": "Matthew",
    "address": "123 Fake St",
    "suburb": "Fitzroy",
    "postcode": "3065",
    "started": "1990-01-01",
    "is_on_lease": "YES",
    "landlord": "John Smith",
    "agent": None,
}
RENT_REDUCTION_ISSUE = {
    "client": "Matthew",
    "topic": "RENT_REDUCTION",
    "stage": None,
    "outcome": None,
    "outcome_notes": "",
    "provided_legal_services": False,
    "answers": {
        "RENT_REDUCTION_ISSUES": ["Another tenant moved out"],
        "RENT_REDUCTION_ISSUE_DESCRIPTION": "Another tenant moved out coz they lost their job and I cannot afford the rent",
        "RENT_REDUCTION_ISSUE_START": "2020-08-02",
        "RENT_REDUCTION_IS_NOTICE_TO_VACATE": True,
    },
}
RENT_REDUCTION_UPLOADS = [
    "380aeaa4-c767-4a9b-90ad-b4d5b4e16859",
    "1f5f6874-9af3-4996-ab8c-022e3877f50f",
]

PROCESS_TESTS = (
    # answers, expected_client, expected_landlord, expected_agent, expected_tenancy, expected_issue
    (
        REPAIRS_ANSWERS,
        REPAIRS_CLIENT,
        REPAIRS_LANDLORD,
        REPAIRS_AGENT,
        REPAIRS_TENANCY,
        REPAIRS_ISSUE,
        REPAIRS_UPLOADS,
    ),
    (
        EVICTIONS_ANSWERS,
        EVICTIONS_CLIENT,
        EVICTIONS_LANDLORD,
        EVICTIONS_AGENT,
        EVICTIONS_TENANCY,
        EVICTIONS_ISSUE,
        EVICTIONS_UPLOADS,
    ),
    (
        RENT_REDUCTION_ANSWERS,
        RENT_REDUCTION_CLIENT,
        RENT_REDUCTION_LANDLORD,
        RENT_REDUCTION_AGENT,
        RENT_REDUCTION_TENANCY,
        RENT_REDUCTION_ISSUE,
        RENT_REDUCTION_UPLOADS,
    ),
)


@pytest.mark.django_db
@pytest.mark.parametrize(
    ",".join(
        [
            "answers",
            "expected_client",
            "expected_landlord",
            "expected_agent",
            "expected_tenancy",
            "expected_issue",
            "expected_uploads",
        ]
    ),
    PROCESS_TESTS,
)
def test_process_submission(
    answers,
    expected_client,
    expected_landlord,
    expected_agent,
    expected_tenancy,
    expected_issue,
    expected_uploads,
):
    """
    Ensure that intake form submissions can be processed,
    """
    # Create some file uploads that we can associate with the issue.
    for upload_id in expected_uploads:
        FileUploadFactory(id=upload_id, issue=None)

    assert Client.objects.count() == 0
    assert Person.objects.count() == 0
    assert Tenancy.objects.count() == 0
    assert Issue.objects.count() == 0
    assert FileUpload.objects.count() == len(expected_uploads)

    sub = Submission.objects.create(answers=answers)
    process_submission(sub.pk)

    expected_num_persons = 0
    if expected_landlord:
        expected_num_persons += 1
    if expected_agent:
        expected_num_persons += 1

    assert Person.objects.count() == expected_num_persons
    assert Client.objects.count() == 1
    assert Tenancy.objects.count() == 1
    assert Issue.objects.count() == 1
    assert FileUpload.objects.count() == len(expected_uploads)

    # Check client was created with correct data
    client = Client.objects.last()
    for k, v in expected_client.items():
        if k == "date_of_birth":
            assert _format_datetime(getattr(client, k)) == v, k
        else:
            assert getattr(client, k) == v, k

    tenancy = Tenancy.objects.last()
    for k, v in expected_tenancy.items():
        if k == "started":
            assert _format_datetime(getattr(tenancy, k)) == v, k
        elif k in ["landlord", "agent"] and v:
            getattr(tenancy, k).full_name == v, k
        elif k == "client":
            getattr(tenancy, k).first_name == v, k
        else:
            assert getattr(tenancy, k) == v, k

    if expected_agent:
        agent = Person.objects.get(email=expected_agent["email"])
        for k, v in expected_agent.items():
            assert getattr(agent, k) == v, k
    else:
        assert tenancy.agent is None

    if expected_landlord:
        landlord = Person.objects.get(email=expected_landlord["email"])
        for k, v in expected_landlord.items():
            assert getattr(landlord, k) == v, k
    else:
        assert tenancy.landlord is None

    issue = Issue.objects.last()
    for k, v in expected_issue.items():
        if k == "client":
            getattr(issue, k).first_name == v, k
    else:
        assert getattr(issue, k) == v, k

    for upload in FileUpload.objects.all():
        assert str(upload.id) in expected_uploads
        assert upload.issue == issue


def _format_datetime(dt):
    dt = timezone.make_naive(dt)
    return datetime.strftime(dt, "%Y-%m-%d")
