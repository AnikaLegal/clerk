from datetime import datetime

import pytest
from django.utils import timezone

from core.factories import FileUploadFactory
from core.models import Client, FileUpload, Issue, Person, Submission, Tenancy
from core.models.upload import FileUpload
from core.services.submission import process_submission

ANSWERS = {
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


@pytest.mark.django_db
def test_process_submission():
    """
    Ensure that intake form submissions can be processed,
    """
    # Create some file uploads that we can associate with the issue.
    FileUploadFactory(id="e249c2c2-15ed-4609-865f-c2109f06f6f8", issue=None)
    assert Client.objects.count() == 0
    assert Person.objects.count() == 0
    assert Tenancy.objects.count() == 0
    assert Issue.objects.count() == 0
    assert FileUpload.objects.count() == 1

    sub = Submission.objects.create(answers=ANSWERS)
    process_submission(sub.pk)

    assert Person.objects.count() == 1
    assert Client.objects.count() == 1
    assert Tenancy.objects.count() == 1
    assert Issue.objects.count() == 1
    assert FileUpload.objects.count() == 1
