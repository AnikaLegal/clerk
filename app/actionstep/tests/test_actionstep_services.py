from unittest import mock

import pytest

from core.factories import IssueFactory, ClientFactory, TenancyFactory
from core.models.issue import Issue
from actionstep.services.actionstep import _send_issue_actionstep


@mock.patch("actionstep.services.actionstep.ActionstepAPI")
@pytest.mark.django_db
def test_issue_actionstep(mock_api):
    # Create the mock Issue
    client = ClientFactory(
        first_name="Keith",
        last_name="Leonardo",
        email="keith@anikalegal.com",
        phone_number="0412348793",
    )
    TenancyFactory(client=client)
    answers = {"FAVOURITE_ANIMAL": "Cow", "BEST_TRICK": "I can do a backflip."}
    issue = IssueFactory(answers=answers, client=client)

    # Set mock return values for all API calls made in _send_issue_actionstep()
    participant = {
        "id": 11,
        "displayName": "Leonardo, Keith",
        "firstName": "Keith",
        "lastName": "Leonardo",
        "phone1Number": None,  # Business
        "phone2Number": None,  # Mobile
        "phone3Number": None,  # Home
        "email": "keith@anikalegal.com",
    }
    filenote = {
        "id": 1234,
        "enteredTimestamp": "2020-07-02T17:35:36+12:00",
        "text": "blah blah blah",
        "enteredBy": "Leonardo, Keith",
        "source": "User",
        "noteTimestamp": "2020-07-02T17:35:22+12:00",
        "links": {"action": "65", "participant": "11"},
    }
    action = {
        "id": 65,
        "name": "Fakey McFakeFake",
        "reference": "R0123",
        "priority": 0,
        "status": "Closed",
        "statusTimestamp": "2020-07-09T19:34:10+12:00",
        "isBillableOverride": None,
        "createdTimestamp": "2020-07-02",
        "modifiedTimestamp": "2020-07-11T07:30:51+12:00",
        "isDeleted": "F",
        "deletedBy": None,
        "deletedTimestamp": None,
        "isFavorite": "F",
        "overrideBillingStatus": None,
        "lastAccessTimestamp": "2020-07-30T16:41:33+12:00",
        "links": {
            "assignedTo": "11",
            "actionType": "28",
            "primaryParticipants": ["159"],
            "relatedActions": None,
        },
    }
    fileschema = {
        "id": 2531,
        "name": "test",
        "modifiedTimestamp": "2020-07-30T16:47:48+12:00",
        "status": "uploaded",
        "keywords": None,
        "summary": None,
        "checkedOutTimestamp": None,
        "fileType": None,
        "checkedOutTo": None,
        "checkedOutEtaTimestamp": None,
        "fileSize": 17,
        "extension": ".txt",
        "sharepointUrl": "https://www.example.com/test.txt",
        "fileName": "65_20200730164748_test.txt",
        "isDeleted": "F",
        "file": "DL::Actions::65::2531",
        "links": {
            "action": "65",
            "checkedOutBy": None,
            "folder": None,
            "createdBy": "11",
        },
    }
    file_upload_status = {"id": "testid", "status": "Uploaded"}
    mock_api.return_value.participants.get_by_email.return_value = participant
    mock_api.return_value.participants.get_or_create.return_value = [participant, True]

    # For testing both if a issue has an action or not
    mock_api.return_value.filenotes.list_by_text_match.side_effect = [[filenote], []]

    mock_api.return_value.actions.get_next_ref.return_value = action["reference"]
    mock_api.return_value.actions.get.return_value = action
    mock_api.return_value.actions.create.return_value = action
    mock_api.return_value.files.upload.return_value = file_upload_status

    # Test when issue has action
    _send_issue_actionstep(issue.pk)
    res_issue = Issue.objects.get(pk=issue.id)
    assert mock_api.return_value.actions.create.call_count == 0
    assert mock_api.return_value.files.upload.call_count == 1
    assert res_issue.is_case_sent

    mock_api.reset_mock()

    # Test when issue has no action
    _send_issue_actionstep(issue.pk)
    res_issue = Issue.objects.get(pk=issue.id)
    assert mock_api.return_value.actions.create.call_count == 1
    assert mock_api.return_value.files.upload.call_count == 1
    assert res_issue.is_case_sent
