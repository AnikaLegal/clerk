from datetime import datetime

import pytest
from django.utils import timezone

from core.factories import ClientFactory
from core.models import Person, Tenancy
from core.services.submission import process_tenancy


BASE_ANSWERS = {
    "ADDRESS": "123 Fake St",
    "IS_ON_LEASE": "YES",
    "POSTCODE": 3065,
    "START_DATE": "2019-01-01",
    "SUBURB": "Fitzroy",
}
BASE_TENANCY = {
    "client": "Matthew",
    "address": "123 Fake St",
    "suburb": "Fitzroy",
    "postcode": "3065",
    "started": "2019-01-01",
    "is_on_lease": "YES",
}


"""
Case 1: Landlord but no agent.
"""
CASE_1_ANSWERS = {
    **BASE_ANSWERS,
    "PROPERTY_MANAGER_IS_AGENT": False,
    "LANDLORD_ADDRESS": "321 Fake St, Fitzroy 3065",
    "LANDLORD_EMAIL": "john.smith@landlord.com",
    "LANDLORD_NAME": "John Smith",
    "LANDLORD_PHONE": "0411111122",
}
CASE_1_LANDLORD = {
    "full_name": "John Smith",
    "email": "john.smith@landlord.com",
    "address": "321 Fake St, Fitzroy 3065",
    "phone_number": "0411111122",
}
CASE_1_AGENT = None
CASE_1_TENANCY = {
    **BASE_TENANCY,
    "landlord": "John Smith",
    "agent": None,
}

"""
Case 2: Agent but partial landlord.
"""
CASE_2_ANSWERS = {
    **BASE_ANSWERS,
    "PROPERTY_MANAGER_IS_AGENT": True,
    "AGENT_ADDRESS": "321 Fake St",
    "AGENT_EMAIL": "sarah.smith@agent.com",
    "AGENT_NAME": "Sarah Smith",
    "AGENT_PHONE": "0411111188",
    "LANDLORD_NAME": "John Smith",
}

CASE_2_LANDLORD = {
    "full_name": "John Smith",
    "email": "",
    "address": "",
    "phone_number": "",
}
CASE_2_AGENT = {
    "full_name": "Sarah Smith",
    "email": "sarah.smith@agent.com",
    "address": "321 Fake St",
    "phone_number": "0411111188",
}
CASE_2_TENANCY = {
    **BASE_TENANCY,
    "landlord": "John Smith",
    "agent": "Sarah Smith",
}


PROCESS_TESTS = (
    (
        CASE_1_ANSWERS,
        CASE_1_LANDLORD,
        CASE_1_AGENT,
        CASE_1_TENANCY,
    ),
    (
        CASE_2_ANSWERS,
        CASE_2_LANDLORD,
        CASE_2_AGENT,
        CASE_2_TENANCY,
    ),
)


@pytest.mark.django_db
@pytest.mark.parametrize(
    ",".join(
        [
            "answers",
            "expected_landlord",
            "expected_agent",
            "expected_tenancy",
        ]
    ),
    PROCESS_TESTS,
)
def test_process_tenancy(
    answers,
    expected_landlord,
    expected_agent,
    expected_tenancy,
):
    """
    Ensure that intake form submissions can be processed into a tenancy.
    """
    client = ClientFactory(first_name="Matthew")
    assert Person.objects.count() == 0
    assert Tenancy.objects.count() == 0
    process_tenancy(answers, client)

    expected_num_persons = 0
    if expected_landlord:
        expected_num_persons += 1
    if expected_agent:
        expected_num_persons += 1

    assert Person.objects.count() == expected_num_persons
    assert Tenancy.objects.count() == 1

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


def _format_datetime(dt):
    dt = timezone.make_naive(dt)
    return datetime.strftime(dt, "%Y-%m-%d")
