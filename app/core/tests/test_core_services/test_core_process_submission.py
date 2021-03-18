from datetime import datetime

import pytest
from core.models.upload import FileUpload

from core.factories import FileUploadFactory
from core.services.submission import process_submission
from core.models import Submission, Client, Person, Tenancy, Issue, FileUpload


"""
Test case #1
- Repairs
- no agent
- speaks Chinese as 1st language
- partner helps with rent
"""
REPAIRS_ANSWERS = {
    "answers": {
        "ISSUES": "REPAIRS",
        "FIRST_NAME": "Matthew",
        "LAST_NAME": "Segal",
        "EMAIL": "mattdsegal@gmail.com",
        "PHONE": "0431417373",
        "AVAILIBILITY": ["WEEK_DAY", "WEEK_EVENING"],
        "REPAIRS_REQUIRED": ["Water", "Roof"],
        "REPAIRS_ISSUE_DESCRIPTION": "Water pipe burst, damaging roof.",
        "REPAIRS_ISSUE_START": "2020-01-01",
        "REPAIRS_ISSUE_PHOTO": [
            {
                "id": "f280feb7-54ed-459f-8057-4603fe7d9996",
                "file": "https://example.com/fde477cab5ba1555caa5983f84f37852.png",
                "issue": None,
            }
        ],
        "RENTAL_CIRCUMSTANCES": "SOLO",
        "IS_ON_LEASE": "YES",
        "START_DATE": "2019-01-01",
        "SUBURB": "Fiztroy",
        "POSTCODE": 3065,
        "ADDRESS": "123 Fake St",
        "PROPERTY_MANAGER_IS_AGENT": False,
        "LANDLORD_NAME": "John Smith",
        "LANDLORD_ADDRESS": "321 Fake St, Fitzroy 3065",
        "LANDLORD_EMAIL": "john.smith@landlord.com",
        "LANDLORD_PHONE": "0411111122",
        "DOB": "1990-08-15",
        "GENDER": "male",
        "IS_ABORIGINAL_OR_TORRES_STRAIT_ISLANDER": False,
        "CAN_SPEAK_NON_ENGLISH": True,
        "FIRST_LANGUAGE": "Chinese",
        "WORK_OR_STUDY_CIRCUMSTANCES": ["STUDENT", "WORKING_PART_TIME"],
        "IS_MULTI_INCOME_HOUSEHOLD": True,
        "WEEKLY_INCOME": 1000,
        "WEEKLY_RENT": 668,
        "NUMBER_OF_DEPENDENTS": 0,
        "SPECIAL_CIRCUMSTANCES": ["CENTRELINK", "PUBLIC_HOUSING"],
        "LEGAL_ACCESS_DIFFICULTIES": ["SUBSTANCE_ABUSE", "DISABILITY"],
        "REFERRER_TYPE": "LEGAL_CENTRE",
        "LEGAL_CENTER_REFERRER": "Justice Connect",
    }
}
REPAIRS_CLIENT = {
    "id": "",
    "first_name": "",
    "last_name": "",
    "email": "",
    "date_of_birth": "",
    "phone_number": "",
    "call_times": "",
    "employment_status": "",
    "special_circumstances": "",
    "weekly_income": "",
    "weekly_rent": "",
    "welfare_reliance": "",
    "gender": "",
    "gender_details": "",
    "can_speak_non_english": "",
    "is_aboriginal_or_torres_strait_islander": "",
    "referrer_type": "",
    "referrer": "",
}
REPAIRS_LANDLORD = {
    "full_name": "John Smith",
    "email": "john.smith@landlord.com",
    "address": "321 Fake St, Fitzroy 3065",
    "phone_number": "0411111122",
}
REPAIRS_AGENT = None
REPAIRS_TENANCY = {
    "client": "Matthew Segal",
    "address": "123 Fake St",
    "suburb": "Fitzroy",
    "postcode": "3065",
    "started": "2019-01-01",
    "is_on_lease": "YES",
    "landlord": "John Smith",
    "agent": None,
}
REPAIRS_ISSUE = {
    "client": "Matthew Segal",
    "topic": "REPAIRS",
    "stage": None,
    "outcome": None,
    "outcome_notes": "",
    "provided_legal_services": False,
    "answers": {
        "REPAIRS_REQUIRED": ["Water", "Roof"],
        "REPAIRS_ISSUE_DESCRIPTION": "Water pipe burst, damaging roof.",
        "REPAIRS_ISSUE_START": "2020-01-01",
        "REPAIRS_ISSUE_PHOTO": [
            {
                "id": "f280feb7-54ed-459f-8057-4603fe7d9996",
                "file": "https://example.com/fde477cab5ba1555caa5983f84f37852.png",
                "issue": None,
            }
        ],
    },
}

"""
Test case #2
- Evictions
- Has agent
- Speaks English as 1st language
- Partner doesn't help with rent (is dependent)
"""
EVICTIONS_ANSWERS = {
    "answers": {
        "ISSUES": "EVICTION",
        "FIRST_NAME": "Matthew",
        "LAST_NAME": "Segal",
        "EMAIL": "mattdsegal@gmail.com",
        "PHONE": "0431417373",
        "AVAILIBILITY": ["WEEK_DAY", "SUNDAY"],
        "EVICTIONS_IS_UNPAID_RENT": True,
        "EVICTIONS_IS_ALREADY_REMOVED": False,
        "EVICTIONS_HAS_NOTICE": True,
        "EVICTIONS_DOCUMENTS_PROVIDED": [
            "Notice to Vacate",
            "Application for a Possession Order",
        ],
        "EVICTIONS_DOCUMENTS_UPLOAD": [
            {
                "id": "ac51e45c-12c2-44e2-acca-bb698d81754f",
                "file": "https://example.com/fbc8205bca9eed4d41d1bdecf9a44fed.pdf",
            },
            {
                "id": "ab365dc1-5aae-4c5e-8528-a5fe08f57d35",
                "file": "https://example.com/d18921c58774870ef2508e1524990228.pdf",
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
        "RENTAL_CIRCUMSTANCES": "PARTNER",
        "IS_ON_LEASE": "YES",
        "START_DATE": "1999-01-01",
        "SUBURB": "Fitzroy",
        "POSTCODE": 3065,
        "ADDRESS": "123 Fake St",
        "PROPERTY_MANAGER_IS_AGENT": True,
        "AGENT_NAME": "Sarah Smith",
        "AGENT_ADDRESS": "321 Fake St",
        "AGENT_EMAIL": "sarah.smith@agent.com",
        "AGENT_PHONE": "0411111188",
        "LANDLORD_NAME": "John Smith",
        "DOB": "1990-02-01",
        "GENDER": "genderqueer",
        "IS_ABORIGINAL_OR_TORRES_STRAIT_ISLANDER": True,
        "CAN_SPEAK_NON_ENGLISH": False,
        "WORK_OR_STUDY_CIRCUMSTANCES": ["WORKING_FULL_TIME"],
        "IS_MULTI_INCOME_HOUSEHOLD": False,
        "WEEKLY_INCOME": 2000,
        "WEEKLY_RENT": 11000,
        "NUMBER_OF_DEPENDENTS": 1,
        "REFERRER_TYPE": "WORD_OF_MOUTH",
    }
}
EVICTIONS_CLIENT = None
EVICTIONS_LANDLORD = None
EVICTIONS_AGENT = None
EVICTIONS_TENANCY = None
EVICTIONS_ISSUE = None

"""
Test case #3
- Rent reduction
- Has no agent
- Speaks Russian as 1st language
- Partner doesn't help with rent (no dependents)
"""
RENT_REDUCTION_ANSWERS = {
    "answers": {
        "ISSUES": "RENT_REDUCTION",
        "FIRST_NAME": "Matthew",
        "LAST_NAME": "Segal",
        "EMAIL": "mattdsegal@gmail.com",
        "PHONE": "0431417373",
        "AVAILIBILITY": ["SUNDAY"],
        "RENT_REDUCTION_ISSUES": ["Another tenant moved out"],
        "RENT_REDUCTION_ISSUE_DESCRIPTION": "Another tenant moved out coz they lost their job and I cannot afford the rent",
        "RENT_REDUCTION_ISSUE_START": "2020-08-02",
        "RENT_REDUCTION_ISSUE_PHOTO": [
            {
                "id": "380aeaa4-c767-4a9b-90ad-b4d5b4e16859",
                "file": "https://example.com/d18921c58774870ef2508e1524990228.pdf",
            }
        ],
        "RENT_REDUCTION_IS_NOTICE_TO_VACATE": True,
        "RENT_REDUCTION_NOTICE_TO_VACATE_DOCUMENT": [
            {
                "id": "1f5f6874-9af3-4996-ab8c-022e3877f50f",
                "file": "https://example.com/d18921c58774870ef2508e1524990228.pdf",
            }
        ],
        "RENTAL_CIRCUMSTANCES": "PARTNER",
        "IS_ON_LEASE": "YES",
        "START_DATE": "1990-01-01",
        "SUBURB": "Fitzroy",
        "POSTCODE": 3065,
        "ADDRESS": "123 Fake St",
        "PROPERTY_MANAGER_IS_AGENT": False,
        "LANDLORD_NAME": "John Smith",
        "LANDLORD_ADDRESS": "321 Fake St, Fitzroy 3065",
        "LANDLORD_EMAIL": "john.smith@landlord.com",
        "LANDLORD_PHONE": "0422211133",
        "DOB": "1990-08-15",
        "GENDER": "omitted",
        "IS_ABORIGINAL_OR_TORRES_STRAIT_ISLANDER": False,
        "CAN_SPEAK_NON_ENGLISH": True,
        "FIRST_LANGUAGE": "Russian",
        "WORK_OR_STUDY_CIRCUMSTANCES": ["LOOKING_FOR_WORK", "STUDENT"],
        "IS_MULTI_INCOME_HOUSEHOLD": False,
        "WEEKLY_INCOME": 1337,
        "WEEKLY_RENT": 1336,
        "NUMBER_OF_DEPENDENTS": 0,
        "SPECIAL_CIRCUMSTANCES": ["REFUGEE"],
        "REFERRER_TYPE": "CHARITY",
        "CHARITY_REFERRER": "Jewish Care",
    }
}
RENT_REDUCTION_CLIENT = None
RENT_REDUCTION_LANDLORD = None
RENT_REDUCTION_AGENT = None
RENT_REDUCTION_TENANCY = None
RENT_REDUCTION_ISSUE = None

PROCESS_TESTS = (
    # answers, expected_client, expected_landlord, expected_agent, expected_tenancy, expected_issue
    (
        REPAIRS_ANSWERS,
        REPAIRS_CLIENT,
        REPAIRS_LANDLORD,
        REPAIRS_AGENT,
        REPAIRS_TENANCY,
        REPAIRS_ISSUE,
    ),
    (
        EVICTIONS_ANSWERS,
        EVICTIONS_CLIENT,
        EVICTIONS_LANDLORD,
        EVICTIONS_AGENT,
        EVICTIONS_TENANCY,
        EVICTIONS_ISSUE,
    ),
    (
        RENT_REDUCTION_ANSWERS,
        RENT_REDUCTION_CLIENT,
        RENT_REDUCTION_LANDLORD,
        RENT_REDUCTION_AGENT,
        RENT_REDUCTION_TENANCY,
        RENT_REDUCTION_ISSUE,
    ),
)


@pytest.mark.django_db
@pytest.mark.parametrize(
    "answers, expected_client, expected_landlord, expected_agent, expected_tenancy, expected_issue",
    PROCESS_TESTS,
)
def test_process_submission(
    answers,
    expected_client,
    expected_landlord,
    expected_agent,
    expected_tenancy,
    expected_issue,
):
    """
    Ensure that intake form submissions can be processed,
    """
    # Create some file uploads that we can associate with the issue.
    upload_1 = FileUploadFactory(id="e249c2c2-15ed-4609-865f-c2109f06f6f8", issue=None)
    upload_2 = FileUploadFactory(id="55bf8c07-5240-4253-9880-58c24f6afd8f", issue=None)
    upload_3 = FileUploadFactory(id="b5871cd9-79ea-4c04-843d-a013c5e0a647", issue=None)
    assert Client.objects.count() == 0
    assert Person.objects.count() == 0
    assert Tenancy.objects.count() == 0
    assert Issue.objects.count() == 0
    assert FileUpload.objects.count() == 3

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
    assert FileUpload.objects.count() == 3

    # # Check client was created
    # client = Client.objects.last()
    # assert client.first_name ==
    # assert client.last_name ==
    # assert client.email ==
    # assert _format_datetime(client.date_of_birth) ==
    # assert client.phone_number ==
    # assert client.call_times ==
    # assert client.gender ==
    # assert client.can_speak_non_english ==
    # assert client.first_langage ==
    # assert client.is_aboriginal_or_torres_strait_islander ==
    # assert client.referrer_type ==
    # assert client.referrer ==

    # assert client.employment_status == "WORKING_FULL_TIME"
    # assert client.welfare_reliance == "SOMEWHAT_RELIANT"
    # assert client.special_circumstances == ["SINGLE_PARENT"]
    # assert client.weekly_income == 700
    # assert client.weekly_rent == 710

    # # Check tenancy was created
    # tenancy = Tenancy.objects.last()
    # assert tenancy.client == client
    # assert tenancy.address == "99 Cool St"
    # assert tenancy.suburb == "Fitzroy"
    # assert tenancy.postcode == "3000"
    # assert _format_datetime(tenancy.started) == "1990-01-01"
    # assert tenancy.is_on_lease is True

    # # Check agent was not created
    # assert tenancy.agent is None

    # # Check landlord was created
    # assert tenancy.landlord.full_name == "John Smith"
    # assert tenancy.landlord.email == "john@smith.com"
    # assert tenancy.landlord.address == "123 Fake St"
    # assert tenancy.landlord.phone_number == "0411111122"

    # # Check issues were created
    # other_issue = Issue.objects.filter(topic="OTHER").last()
    # assert other_issue.client == client
    # assert other_issue.is_open
    # assert other_issue.answers == {
    #     "OTHER_ISSUE_DESCRIPTION": "Lots of mould",
    # }
