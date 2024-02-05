import pytest

import json
from uuid import uuid4
from pathlib import Path

from core.factories import FileUploadFactory
from core.models import Client, FileUpload, Issue, Person, Submission, Tenancy
from core.services.submission import process_submission


def _test_data():
    dir = Path(__file__)
    dir = Path(dir.parent / dir.stem)

    data = []
    for path in sorted(dir.glob("*")):
        if path.is_dir():
            name = path.stem

            file = path / Path("submissions.json")
            submission = json.loads(file.read_text())

            file = path / Path("expected.json")
            expected = json.loads(file.read_text())

            data.append((name, submission, expected))
    return data


@pytest.mark.django_db()
@pytest.mark.parametrize("name, submissions, expected", _test_data())
def test_process_submissions(name, submissions, expected):
    """
    Ensure we have the expected object counts when making submissions.
    """

    for sub in submissions:
        # Create some file uploads that we can associate with the issue.
        id = sub["REPAIRS_ISSUE_PHOTO"][0]["id"]
        FileUploadFactory(id=id, issue=None)

        process_submission(Submission.objects.create(answers=sub).pk)

    assert Client.objects.count() == expected["client"], "unexpected Client count"
    assert Person.objects.count() == expected["person"], "unexpected Person count"
    assert Tenancy.objects.count() == expected["tenancy"], "unexpected Tenancy count"
    assert Issue.objects.count() == expected["issue"], "unexpected Issue count"
    assert (
        FileUpload.objects.count() == expected["file_upload"]
    ), "unexpected FileUpload count"
