import pytest

from unittest import mock
from questions.services.actionstep import _send_submission_actionstep
from questions.tests.factories import SubmissionFactory
from questions.models.submission import Submission    

@mock.patch("questions.services.actionstep.ActionstepAPI")
@pytest.mark.django_db
def test_submission_actionstep(mock_api):
    # Create the mock Submission
    questions = [
        {
            "name": "deets",
            "forms": [
                {
                    "name": "form 1",
                    "fields": [
                        {"name": "CLIENT_NAME", "type": "TEXT", "prompt": "Name?"},
                        {"name": "CLIENT_PHONE", "type": "TEXT", "prompt": "Phone?"},
                        {"name": "CLIENT_EMAIL", "type": "TEXT", "prompt": "Email?"}
                    ]
                }
            ]
        }
    ]
    answers = [
        {"name": "CLIENT_NAME", "answer": "Keith Leonardo"},
        {"name": "CLIENT_PHONE", "answer": "0412 348793"},
        {"name": "CLIENT_EMAIL", "answer": "keith@anikalegal.com"},
    ]
    sub = SubmissionFactory(complete=False, questions=questions, answers=answers)
    
    # Set mock return values for all API calls made in _send_submission_actionstep()
    participant = {
        'id': 11,
        'displayName': 'Leonardo, Keith',
        'firstName': 'Keith',
        'lastName': 'Leonardo',
        'phone1Number': None, # Business
        'phone2Number': None, # Mobile
        'phone3Number': None, # Home
        'email': 'keith@anikalegal.com',
    }
    filenote = {
        'id': 1234,
        'enteredTimestamp': '2020-07-02T17:35:36+12:00',
        'text': 'blah blah blah',
        'enteredBy': 'Leonardo, Keith',
        'source': 'User',
        'noteTimestamp': '2020-07-02T17:35:22+12:00',
        'links': {'action': '65', 'participant': '11'}
    }
    action = {
        'id': 65,
        'name': 'Fakey McFakeFake',
        'reference': 'R0123',
        'priority': 0,
        'status': 'Closed',
        'statusTimestamp': '2020-07-09T19:34:10+12:00',
        'isBillableOverride': None,
        'createdTimestamp': '2020-07-02',
        'modifiedTimestamp': '2020-07-11T07:30:51+12:00',
        'isDeleted': 'F',
        'deletedBy': None,
        'deletedTimestamp': None,
        'isFavorite': 'F',
        'overrideBillingStatus': None,
        'lastAccessTimestamp': '2020-07-30T16:41:33+12:00',
        'links': {'assignedTo': '11',
        'actionType': '28',
        'primaryParticipants': ['159'],
        'relatedActions': None}
    }
    fileschema = {
        'id': 2531,
        'name': 'test',
        'modifiedTimestamp': '2020-07-30T16:47:48+12:00',
        'status': 'uploaded',
        'keywords': None,
        'summary': None,
        'checkedOutTimestamp': None,
        'fileType': None,
        'checkedOutTo': None,
        'checkedOutEtaTimestamp': None,
        'fileSize': 17,
        'extension': '.txt',
        'sharepointUrl': 'https://www.example.com/test.txt',
        'fileName': '65_20200730164748_test.txt',
        'isDeleted': 'F',
        'file': 'DL::Actions::65::2531',
        'links': {
            'action': '65',
            'checkedOutBy': None,
            'folder': None,
            'createdBy': '11'
        }
    }
    mock_api.return_value.participants.get_by_email.return_value = participant
    mock_api.return_value.participants.get_or_create.return_value = [participant, True]
    
    mock_api.return_value.filenotes.list_by_text_match.side_effect = [[filenote], []]

    mock_api.return_value.actions.get_next_ref.return_value = action["reference"]
    mock_api.return_value.actions.get.return_value = action
    mock_api.return_value.actions.create.return_value = action

    # Test if submission has action
    _send_submission_actionstep(sub.pk)
    res_sub = Submission.objects.get(pk=sub.id)
    assert mock_api.return_value.actions.create.call_count == 0
    assert res_sub.is_case_sent

    # Test for if submission has no action
    _send_submission_actionstep(sub.pk)
    res_sub = Submission.objects.get(pk=sub.id)
    assert mock_api.return_value.actions.create.call_count == 1
    assert res_sub.is_case_sent