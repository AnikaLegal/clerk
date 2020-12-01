from unittest import mock

import pytest
from core.models.upload import FileUpload

from core.factories import FileUploadFactory
from core.services.submission import process_submission
from core.models import Submission, Client, Person, Tenancy, Issue, FileUpload


@pytest.mark.django_db
def test_process_submission():
    repairs_photo = FileUploadFactory(
        id="e249c2c2-15ed-4609-865f-c2109f06f6f8", issue=None
    )
    rent_photo = FileUploadFactory(
        id="55bf8c07-5240-4253-9880-58c24f6afd8f", issue=None
    )
    notice_photo = FileUploadFactory(
        id="b5871cd9-79ea-4c04-843d-a013c5e0a647", issue=None
    )
    assert Client.objects.count() == 0
    assert Person.objects.count() == 0
    assert Tenancy.objects.count() == 0
    assert Issue.objects.count() == 0
    assert FileUpload.objects.count() == 3

    sub = Submission.objects.create(answers=ANSWERS)
    process_submission(sub.pk)

    assert Client.objects.count() == 1
    assert Person.objects.count() == 1
    assert Tenancy.objects.count() == 1
    assert Issue.objects.count() == 3
    assert FileUpload.objects.count() == 3

    # Check client was created
    client = Client.objects.last()
    assert client.first_name == "Matt"
    assert client.last_name == "Segal"
    assert client.email == "mattdsegal2@gmail.com"
    # assert client.date_of_birth # TODO
    assert client.phone_number == "0431417373"
    assert client.call_time == "SUNDAY"
    assert client.gender == "omitted"
    assert client.gender_details is None
    assert client.can_speak_non_english is False
    assert client.is_aboriginal_or_torres_strait_islander is False
    assert client.referrer_type == "CHARITY"
    assert client.referrer == "Jewish Care"

    # Check agent was created
    landlord = Person.objects.last()
    assert landlord.full_name == "Joe Blowzini"
    assert landlord.email == "joe@joemail.co"
    assert landlord.address == "123 Joe St"
    assert landlord.phone_number == "0411111166"

    # Check tenancy was created
    tenancy = Tenancy.objects.last()
    assert tenancy.client == client
    assert tenancy.landlord == landlord
    assert tenancy.agent is None

    assert tenancy.address == "3/71 Rose St"
    assert tenancy.suburb == "Fitzroy"
    assert tenancy.postcode == "3000"
    # assert tenancy.started == "" # TODO
    assert tenancy.is_on_lease is True

    # Check issues were created
    repairs_issue = Issue.objects.filter(topic="REPAIRS").last()
    assert repairs_issue.client == client
    assert repairs_issue.is_open
    assert repairs_issue.answers == {
        "REPAIRS_REQUIRED": ["Water", "Laundry"],
        "REPAIRS_ISSUE_START": "1990-01-02",
        "REPAIRS_ISSUE_DESCRIPTION": "Laundry is bad",
    }

    rent_issue = Issue.objects.filter(topic="RENT_REDUCTION").last()
    assert rent_issue.client == client
    assert rent_issue.is_open
    assert rent_issue.answers == {
        "RENT_REDUCTION_ISSUES": ["Unable to work", "Another tenant moved out"],
        "RENT_REDUCTION_ISSUE_START": "1990-01-03",
        "RENT_REDUCTION_ISSUE_DESCRIPTION": "I can't work cos sad",
        "RENT_REDUCTION_IS_NOTICE_TO_VACATE": True,
    }

    other_issue = Issue.objects.filter(topic="OTHER").last()
    assert other_issue.client == client
    assert other_issue.is_open
    assert other_issue.answers == {
        "OTHER_ISSUE_DESCRIPTION": "I also have a dog",
    }

    # Check file uploads got associated with issues.
    repairs_photo.refresh_from_db()
    rent_photo.refresh_from_db()
    notice_photo.refresh_from_db()
    assert repairs_photo.issue == repairs_issue
    assert rent_photo.issue == rent_issue
    assert notice_photo.issue == rent_issue


ANSWERS = {
    # Client info
    "DOB": "1990-08-15",
    "EMAIL": "mattdsegal2@gmail.com",
    "PHONE": "0431417373",
    "GENDER": "omitted",
    "LAST_NAME": "Segal",
    "FIRST_NAME": "Matt",
    "CAN_SPEAK_NON_ENGLISH": False,
    "REFERRER_TYPE": "CHARITY",
    "HOUSING_SERVICE_REFERRER": None,
    "LEGAL_CENTER_REFERRER": None,
    "GENDER_DETAILS": None,
    "SOCIAL_REFERRER": None,
    "CHARITY_REFERRER": "Jewish Care",
    "AVAILIBILITY": "SUNDAY",
    "IS_ABORIGINAL_OR_TORRES_STRAIT_ISLANDER": False,
    # Tenancy info
    "SUBURB": "Fitzroy",
    "POSTCODE": "3000",
    "ADDRESS": "3/71 Rose St",
    "START_DATE": "1990-01-01",
    "IS_ON_LEASE": True,
    # Agent
    "PROPERTY_MANAGER_IS_AGENT": False,
    "AGENT_NAME": None,
    "AGENT_EMAIL": None,
    "AGENT_PHONE": None,
    "AGENT_ADDRESS": None,
    # Landlord
    "LANDLORD_EMAIL": "joe@joemail.co",
    "LANDLORD_PHONE": "0411111166",
    "LANDLORD_NAME": "Joe Blowzini",
    "LANDLORD_ADDRESS": "123 Joe St",
    # Issues
    "ISSUES": ["RENT_REDUCTION", "REPAIRS", "OTHER"],
    # Repairs
    "REPAIRS_REQUIRED": ["Water", "Laundry"],
    "REPAIRS_ISSUE_START": "1990-01-02",
    "REPAIRS_ISSUE_DESCRIPTION": "Laundry is bad",
    "REPAIRS_ISSUE_PHOTO": [
        {
            "id": "e249c2c2-15ed-4609-865f-c2109f06f6f8",
            "file": "https://example.com/aa38178f59af1c64329290fb3117b005.png",
            "issue": None,
        }
    ],
    # Rent reduction
    "RENT_REDUCTION_ISSUES": ["Unable to work", "Another tenant moved out"],
    "RENT_REDUCTION_ISSUE_START": "1990-01-03",
    "RENT_REDUCTION_ISSUE_DESCRIPTION": "I can't work cos sad",
    "RENT_REDUCTION_IS_NOTICE_TO_VACATE": True,
    "RENT_REDUCTION_ISSUE_PHOTO": [
        {
            "id": "55bf8c07-5240-4253-9880-58c24f6afd8f",
            "file": "https://example.com/56f8d89320cd58c82cccf641adf43335.png",
            "issue": None,
        }
    ],
    "RENT_REDUCTION_NOTICE_TO_VACATE_DOCUMENT": [
        {
            "id": "b5871cd9-79ea-4c04-843d-a013c5e0a647",
            "file": "https://example.com/fde477cab5ba1555caa5983f84f37852.png",
            "issue": None,
        }
    ],
    # Other issue
    "OTHER_ISSUE_DESCRIPTION": "I also have a dog",
    # Unused
    "IS_TENANT": True,
    "RENT_REDUCTION_OUTRO": None,
    "IS_VICTORIAN": True,
    "SUBMIT": None,
    "INTRO": None,
    "OTHER_INTRO": None,
    "OTHER_OUTRO": None,
    "CONTACT_INTRO": None,
    "REPAIRS_OUTRO": None,
    "REPAIRS_INTRO": None,
    "PROPERTY_MANAGER_INTRO": None,
    "RENT_REDUCTION_INTRO": None,
}
