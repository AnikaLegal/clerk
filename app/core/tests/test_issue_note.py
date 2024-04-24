import pytest

from core.factories import IssueFactory
from core.models import IssueNote

# TODO: add tests for when notes should be added.


@pytest.mark.django_db
@pytest.mark.enable_signals
def test_issue_note_not_created_on_issue_create():
    """
    Ensure an issue note is NOT created when an issue is created.
    """
    issue = IssueFactory()
    assert IssueNote.objects.count() == 0
