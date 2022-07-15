from datetime import datetime

import pytest
from django.utils import timezone

from core.models import Client
from core.services.submission import process_client


BASE_ANSWERS = {
    "DOB": "1990-08-15",
    "EMAIL": "mattdsegal@gmail.com",
    "FIRST_NAME": "Matthew",
    "LAST_NAME": "Segal",
    "PHONE": "0431417373",
    "INTERPRETER": True,
    "CENTRELINK_SUPPORT": True,
    "ELIGIBILITY_NOTES": None,
}
BASE_CLIENT = {
    "date_of_birth": "1990-08-15",
    "email": "mattdsegal@gmail.com",
    "first_name": "Matthew",
    "last_name": "Segal",
    "phone_number": "0431417373",
    "requires_interpreter": True,
    "centrelink_support": True,
    "eligibility_notes": "",
}


"""
Case 1:
- speaks Chinese as 1st language
- partner helps with rent
"""
CASE_1_ANSWERS = {
    **BASE_ANSWERS,
    "INTERPRETER": False,
    "CENTRELINK_SUPPORT": False,
    "ELIGIBILITY_NOTES": "I need help pls.",
    "AVAILIBILITY": ["WEEK_DAY", "WEEK_EVENING"],
    "CAN_SPEAK_NON_ENGLISH": True,
    "FIRST_LANGUAGE": "Chinese",
    "GENDER": "male",
    "IS_ABORIGINAL_OR_TORRES_STRAIT_ISLANDER": False,
    "LEGAL_CENTER_REFERRER": "Justice Connect",
    "NUMBER_OF_DEPENDENTS": 0,
    "REFERRER_TYPE": "LEGAL_CENTRE",
    "RENTAL_CIRCUMSTANCES": "PARTNER",
    "WEEKLY_HOUSEHOLD_INCOME": 1000,
    "WORK_OR_STUDY_CIRCUMSTANCES": ["STUDENT", "WORKING_PART_TIME", "PARENT"],
    "ELIGIBILITY_CIRCUMSTANCES": ["SUBSTANCE_ABUSE", "PHYSICAL_DISABILITY"],
}
CASE_1_CLIENT = {
    **BASE_CLIENT,
    "requires_interpreter": False,
    "centrelink_support": False,
    "eligibility_notes": "I need help pls.",
    "call_times": ["WEEK_DAY", "WEEK_EVENING"],
    "employment_status": ["STUDENT", "WORKING_PART_TIME", "PARENT"],
    "gender": "male",
    "is_aboriginal_or_torres_strait_islander": False,
    "number_of_dependents": 0,
    "primary_language_non_english": True,
    "primary_language": "Chinese",
    "referrer_type": "LEGAL_CENTRE",
    "referrer": "Justice Connect",
    "rental_circumstances": "PARTNER",
    "eligibility_circumstances": ["SUBSTANCE_ABUSE", "PHYSICAL_DISABILITY"],
    "weekly_income": 1000,
}

"""
Test case #2
- Speaks English as 1st language
- Partner doesn't help with rent (is dependent)
- Is aboriginal or TSI
"""
CASE_2_ANSWERS = {
    **BASE_ANSWERS,
    "AVAILIBILITY": ["WEEK_DAY", "SUNDAY"],
    "CAN_SPEAK_NON_ENGLISH": False,
    "FIRST_LANGUAGE": None,
    "FIRST_NAME": "Matthew",
    "GENDER": "genderqueer",
    "IS_ABORIGINAL_OR_TORRES_STRAIT_ISLANDER": True,
    "NUMBER_OF_DEPENDENTS": 1,
    "REFERRER_TYPE": "WORD_OF_MOUTH",
    "RENTAL_CIRCUMSTANCES": "PARTNER",
    "WEEKLY_HOUSEHOLD_INCOME": 2000,
    "WORK_OR_STUDY_CIRCUMSTANCES": ["WORKING_FULL_TIME"],
}
CASE_2_CLIENT = {
    **BASE_CLIENT,
    "call_times": ["WEEK_DAY", "SUNDAY"],
    "employment_status": ["WORKING_FULL_TIME"],
    "gender": "genderqueer",
    "is_aboriginal_or_torres_strait_islander": True,
    "eligibility_circumstances": [],
    "number_of_dependents": 1,
    "primary_language_non_english": False,
    "primary_language": "",
    "referrer_type": "WORD_OF_MOUTH",
    "referrer": "",
    "rental_circumstances": "PARTNER",
    "weekly_income": 2000,
}


"""
Test case #3
- Speaks Russian as 1st language
- Partner doesn't help with rent (no dependents)
"""
CASE_3_ANSWERS = {
    **BASE_ANSWERS,
    "AVAILIBILITY": ["SUNDAY"],
    "CAN_SPEAK_NON_ENGLISH": True,
    "CHARITY_REFERRER": "Jewish Care",
    "FIRST_LANGUAGE": "Russian",
    "GENDER": "omitted",
    "IS_ABORIGINAL_OR_TORRES_STRAIT_ISLANDER": False,
    "NUMBER_OF_DEPENDENTS": 0,
    "REFERRER_TYPE": "CHARITY",
    "RENTAL_CIRCUMSTANCES": "SOLO",
    "WEEKLY_HOUSEHOLD_INCOME": 1337,
    "SUBURB": "Fitzroy",
    "WORK_OR_STUDY_CIRCUMSTANCES": ["LOOKING_FOR_WORK", "STUDENT"],
    "ELIGIBILITY_CIRCUMSTANCES": ["VISA"],
}
CASE_3_CLIENT = {
    **BASE_CLIENT,
    "call_times": ["SUNDAY"],
    "employment_status": ["LOOKING_FOR_WORK", "STUDENT"],
    "gender": "omitted",
    "is_aboriginal_or_torres_strait_islander": False,
    "number_of_dependents": 0,
    "primary_language_non_english": True,
    "primary_language": "Russian",
    "referrer_type": "CHARITY",
    "referrer": "Jewish Care",
    "rental_circumstances": "SOLO",
    "weekly_income": 1337,
    "eligibility_circumstances": ["VISA"],
}


"""
Test case #3
- Bonds
- Mostly same as repairs
"""
CASE_4_ANSWERS = {
    **BASE_ANSWERS,
    "AVAILIBILITY": ["WEEK_DAY", "WEEK_EVENING"],
    "CAN_SPEAK_NON_ENGLISH": True,
    "FIRST_LANGUAGE": "Chinese",
    "GENDER": "male",
    "IS_ABORIGINAL_OR_TORRES_STRAIT_ISLANDER": False,
    "LEGAL_CENTER_REFERRER": "Justice Connect",
    "NUMBER_OF_DEPENDENTS": 0,
    "REFERRER_TYPE": "LEGAL_CENTRE",
    "RENTAL_CIRCUMSTANCES": "PARTNER",
    "WEEKLY_HOUSEHOLD_INCOME": 1000,
    "WORK_OR_STUDY_CIRCUMSTANCES": ["STUDENT", "WORKING_PART_TIME"],
    "ELIGIBILITY_CIRCUMSTANCES": ["SUBSTANCE_ABUSE"],
}
CASE_4_CLIENT = {
    **BASE_CLIENT,
    "call_times": ["WEEK_DAY", "WEEK_EVENING"],
    "employment_status": ["STUDENT", "WORKING_PART_TIME"],
    "gender": "male",
    "is_aboriginal_or_torres_strait_islander": False,
    "number_of_dependents": 0,
    "primary_language_non_english": True,
    "primary_language": "Chinese",
    "referrer_type": "LEGAL_CENTRE",
    "referrer": "Justice Connect",
    "rental_circumstances": "PARTNER",
    "weekly_income": 1000,
    "eligibility_circumstances": ["SUBSTANCE_ABUSE"],
}


PROCESS_TESTS = [
    # answers, expected_client, expected_landlord, expected_agent, expected_tenancy, expected_issue
    (CASE_1_ANSWERS, CASE_1_CLIENT),
    (CASE_2_ANSWERS, CASE_2_CLIENT),
    (CASE_3_ANSWERS, CASE_3_CLIENT),
    (CASE_4_ANSWERS, CASE_4_CLIENT),
]


@pytest.mark.django_db
@pytest.mark.parametrize(
    ",".join(
        [
            "answers",
            "expected_client",
        ]
    ),
    PROCESS_TESTS,
)
def test_process_client(answers, expected_client):
    """
    Ensure that intake form submissions can be processed into a client.
    """
    assert Client.objects.count() == 0
    process_client(answers)
    assert Client.objects.count() == 1

    # Check client was created with correct data
    client = Client.objects.last()
    for k, v in expected_client.items():
        if k == "date_of_birth":
            assert _format_datetime(getattr(client, k)) == v, k
        else:
            assert getattr(client, k) == v, k


def _format_datetime(dt):
    dt = timezone.make_naive(dt)
    return datetime.strftime(dt, "%Y-%m-%d")
