from re import I
import pytest

from core.models.issue import CaseTopic
from core.factories import IssueFactory


@pytest.mark.django_db
def test_get_next_fileref__first_one():
    issue = IssueFactory(topic=CaseTopic.REPAIRS)
    assert issue.fileref == "R0001"


@pytest.mark.django_db
def test_get_next_fileref__with_prior_filerefs():
    IssueFactory(topic=CaseTopic.REPAIRS, fileref="R0023")
    IssueFactory(topic=CaseTopic.REPAIRS, fileref="R0001")
    IssueFactory(topic=CaseTopic.BONDS, fileref="B0004")
    IssueFactory(topic=CaseTopic.BONDS, fileref="B0056")
    issue = IssueFactory(topic=CaseTopic.REPAIRS)
    assert issue.fileref == "R0024"


@pytest.mark.django_db
def test_get_next_fileref__with_prior_filerefs__over_9999():
    IssueFactory(topic=CaseTopic.REPAIRS, fileref="R9999")
    IssueFactory(topic=CaseTopic.REPAIRS, fileref="R0001")
    IssueFactory(topic=CaseTopic.BONDS, fileref="B0004")
    IssueFactory(topic=CaseTopic.BONDS, fileref="B0056")
    issue = IssueFactory(topic=CaseTopic.REPAIRS)
    assert issue.fileref == "R10000"
