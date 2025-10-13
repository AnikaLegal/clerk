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
    "INTERPRETER": "YES_WRITTEN_AND_SPOKEN",
    "CENTRELINK_SUPPORT": True,
    "ELIGIBILITY_NOTES": None,
}
BASE_CLIENT = {
    "date_of_birth": "1990-08-15",
    "email": "mattdsegal@gmail.com",
    "first_name": "Matthew",
    "last_name": "Segal",
    "phone_number": "0431417373",
    "requires_interpreter": "YES_WRITTEN_AND_SPOKEN",
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
    "PREFERRED_NAME": "Matt",
    "INTERPRETER": "NO",
    "CENTRELINK_SUPPORT": False,
    "ELIGIBILITY_NOTES": "I need help pls.",
    "AVAILABILITY": ["WEEK_DAY", "WEEK_EVENING"],
    "CAN_SPEAK_NON_ENGLISH": True,
    "FIRST_LANGUAGE": "Chinese",
    "GENDER": "male",
    "IS_ABORIGINAL_OR_TORRES_STRAIT_ISLANDER": "NO",
    "NUMBER_OF_DEPENDENTS": 0,
    "WEEKLY_HOUSEHOLD_INCOME": 1000,
    "ELIGIBILITY_CIRCUMSTANCES": ["SUBSTANCE_ABUSE", "PHYSICAL_DISABILITY"],
}
CASE_1_CLIENT = {
    **BASE_CLIENT,
    "preferred_name": "Matt",
    "requires_interpreter": "NO",
    "centrelink_support": False,
    "eligibility_notes": "I need help pls.",
    "call_times": ["WEEK_DAY", "WEEK_EVENING"],
    "gender": "male",
    "is_aboriginal_or_torres_strait_islander": "NO",
    "number_of_dependents": 0,
    "primary_language_non_english": True,
    "primary_language": "Chinese",
    "eligibility_circumstances": ["SUBSTANCE_ABUSE", "PHYSICAL_DISABILITY"],
}

"""
Test case #2
- Speaks English as 1st language
- Partner doesn't help with rent (is dependent)
- Is aboriginal or TSI
"""
CASE_2_ANSWERS = {
    **BASE_ANSWERS,
    "PREFERRED_NAME": None,
    "AVAILABILITY": ["WEEK_DAY", "SUNDAY"],
    "CAN_SPEAK_NON_ENGLISH": False,
    "FIRST_LANGUAGE": None,
    "FIRST_NAME": "Matthew",
    "GENDER": "genderqueer",
    "IS_ABORIGINAL_OR_TORRES_STRAIT_ISLANDER": "YES_ABORIGINAL",
    "NUMBER_OF_DEPENDENTS": 1,
    "WEEKLY_HOUSEHOLD_INCOME": 2000,
}
CASE_2_CLIENT = {
    **BASE_CLIENT,
    "preferred_name": None,
    "call_times": ["WEEK_DAY", "SUNDAY"],
    "gender": "genderqueer",
    "is_aboriginal_or_torres_strait_islander": "YES_ABORIGINAL",
    "eligibility_circumstances": [],
    "number_of_dependents": 1,
    "primary_language_non_english": False,
    "primary_language": "",
}


"""
Test case #3
- Speaks Russian as 1st language
- Partner doesn't help with rent (no dependents)
"""
CASE_3_ANSWERS = {
    **BASE_ANSWERS,
    "PREFERRED_NAME": None,
    "AVAILABILITY": ["SUNDAY"],
    "CAN_SPEAK_NON_ENGLISH": True,
    "FIRST_LANGUAGE": "Russian",
    "GENDER": "omitted",
    "IS_ABORIGINAL_OR_TORRES_STRAIT_ISLANDER": "PREFER_NOT_TO_ANSWER",
    "NUMBER_OF_DEPENDENTS": 0,
    "WEEKLY_HOUSEHOLD_INCOME": 1337,
    "SUBURB": "Fitzroy",
    "ELIGIBILITY_CIRCUMSTANCES": ["VISA"],
}
CASE_3_CLIENT = {
    **BASE_CLIENT,
    "preferred_name": None,
    "call_times": ["SUNDAY"],
    "gender": "omitted",
    "is_aboriginal_or_torres_strait_islander": "PREFER_NOT_TO_ANSWER",
    "number_of_dependents": 0,
    "primary_language_non_english": True,
    "primary_language": "Russian",
    "eligibility_circumstances": ["VISA"],
}


"""
Test case #3
- Bonds
- Mostly same as repairs
"""
CASE_4_ANSWERS = {
    **BASE_ANSWERS,
    "PREFERRED_NAME": "Matt",
    "AVAILABILITY": ["WEEK_DAY", "WEEK_EVENING"],
    "CAN_SPEAK_NON_ENGLISH": True,
    "FIRST_LANGUAGE": "Chinese",
    "GENDER": "male",
    "IS_ABORIGINAL_OR_TORRES_STRAIT_ISLANDER": "NO",
    "NUMBER_OF_DEPENDENTS": 0,
    "WEEKLY_HOUSEHOLD_INCOME": 1000,
    "ELIGIBILITY_CIRCUMSTANCES": ["SUBSTANCE_ABUSE"],
}
CASE_4_CLIENT = {
    **BASE_CLIENT,
    "preferred_name": "Matt",
    "call_times": ["WEEK_DAY", "WEEK_EVENING"],
    "gender": "male",
    "is_aboriginal_or_torres_strait_islander": "NO",
    "number_of_dependents": 0,
    "primary_language_non_english": True,
    "primary_language": "Chinese",
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
