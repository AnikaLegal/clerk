import pytest

from core.models.issue import CaseTopic
from core.factories import IssueFactory


@pytest.mark.django_db
def test_fileref_prefix():
    for topic, _ in CaseTopic.CHOICES:
        issue = IssueFactory(topic=topic)

        if topic == CaseTopic.RENT_REDUCTION:
            # Special case
            assert issue.fileref[0] == "C"
        else:
            assert issue.fileref[0] == topic[0]


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
def test_get_next_fileref__with_different_eviction_topic_has_same_prefix():
    issue_1 = IssueFactory(topic=CaseTopic.EVICTION_ARREARS)
    issue_2 = IssueFactory(topic=CaseTopic.EVICTION_RETALIATORY)
    assert issue_1.fileref == "E0001"
    assert issue_2.fileref == "E0002"


@pytest.mark.django_db
def test_get_next_fileref__with_prior_filerefs__over_9999():
    IssueFactory(topic=CaseTopic.REPAIRS, fileref="R9999")
    IssueFactory(topic=CaseTopic.REPAIRS, fileref="R0001")
    IssueFactory(topic=CaseTopic.BONDS, fileref="B0004")
    IssueFactory(topic=CaseTopic.BONDS, fileref="B0056")
    issue = IssueFactory(topic=CaseTopic.REPAIRS)
    assert issue.fileref == "R10000"
