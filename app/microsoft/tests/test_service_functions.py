from unittest.mock import patch

import pytest
from core.factories import DocumentTemplateFactory, IssueFactory, UserFactory
from microsoft.service import (
    add_user_to_case,
    get_case_folder_info,
    remove_user_from_case,
    set_up_coordinator,
    set_up_new_case,
    set_up_new_user,
    tear_down_coordinator,
)
from microsoft.storage import MSGraphStorage


@pytest.fixture
def mock_api():
    # Mock the MSGraphAPI instance
    with patch("microsoft.service.MSGraphAPI") as mock_msgraph_api:
        mock_instance = mock_msgraph_api.return_value
        mock_instance.is_available.return_value = True
        yield mock_instance


@pytest.mark.django_db
def test_set_up_new_user_A(mock_api):
    """Check service function does not create MS account or assign license for existing user."""
    user = UserFactory()
    mock_api.user.get.return_value = {
        f"Microsoft Account already exists for {user.email}"
    }

    set_up_new_user(user)

    mock_api.user.get.assert_called_once_with(user.email)
    mock_api.user.create.assert_not_called()
    mock_api.user.assign_license.assert_not_called()


@pytest.mark.django_db
def test_set_up_new_user_B(mock_api):
    """Check service function creates MS account and assigns license for new user."""
    user = UserFactory()
    mock_api.user.get.return_value = None
    mock_api.user.create.return_value = user, "open sesame"

    password = set_up_new_user(user)

    mock_api.user.get.assert_called_once_with(user.email)
    mock_api.user.create.assert_called_once_with(
        user.first_name, user.last_name, user.email
    )
    mock_api.user.assign_license.assert_called_once_with(user.email)
    assert password == "open sesame"


@pytest.mark.django_db
def test_set_up_new_case(mock_api):
    """Check service function creates new case folder and places it inside parent folder."""
    issue = IssueFactory()

    with patch.object(MSGraphStorage, "_get_file_info", return_value={}):
        template = DocumentTemplateFactory(topic=issue.topic, subtopic=issue.subtopic)

    mock_api.folder.get_child_if_exists.return_value = None
    mock_api.folder.create_folder.return_value = {"id": "folder_id"}

    set_up_new_case(issue)

    mock_api.folder.copy.assert_called_once_with(
        template.api_file_path, template.name, "folder_id"
    )


@pytest.mark.django_db
def test_add_user_to_case(mock_api):
    """Check service function gives user write permissions to existing case folder."""
    user = UserFactory()
    issue = IssueFactory()

    add_user_to_case(user, issue)

    mock_api.folder.create_permissions.assert_called_once_with(
        f"cases/{issue.id}", "write", [user.email]
    )


@pytest.mark.django_db
def test_remove_user_from_case_A(mock_api):
    """Check service function when there are no permissions on the case folder."""
    user = UserFactory()
    issue = IssueFactory()
    mock_api.folder.list_permissions.return_value = None

    remove_user_from_case(user, issue)

    mock_api.folder.list_permissions.assert_called_once_with(f"cases/{issue.id}")
    mock_api.folder.delete_permission.assert_not_called()


@pytest.mark.django_db
def test_remove_user_from_case_B(mock_api):
    """Check service function when there are permissions on the case folder that don't belong to our user."""
    user = UserFactory(email="donald.duck@anikalegal.com")
    issue = IssueFactory()
    mock_api.folder.list_permissions.return_value = [
        ("666", {"user": {"email": "bugs.bunny@anikalegal.com"}})
    ]

    remove_user_from_case(user, issue)

    mock_api.folder.list_permissions.assert_called_once_with(f"cases/{issue.id}")
    mock_api.folder.delete_permission.assert_not_called()


@pytest.mark.django_db
def test_remove_user_from_case_C(mock_api):
    """Check service function when there are permissions on the case folder belonging to our user."""
    user = UserFactory(email="donald.duck@anikalegal.com")
    issue = IssueFactory()
    mock_api.folder.list_permissions.return_value = [
        ("666", {"user": {"email": "donald.duck@anikalegal.com"}})
    ]

    remove_user_from_case(user, issue)

    mock_api.folder.list_permissions.assert_called_once_with(f"cases/{issue.id}")
    mock_api.folder.delete_permission.assert_called_once_with(
        f"cases/{issue.id}", "666"
    )


@pytest.mark.django_db
def test_get_case_folder_info_A(mock_api):
    """Check service function when the case folder doesn't exist."""
    issue = IssueFactory()
    mock_api.folder.get_children.return_value = []
    mock_api.folder.get.return_value = None

    documents, url = get_case_folder_info(issue)

    mock_api.folder.get_children.assert_called_once_with(f"cases/{issue.id}")
    mock_api.folder.get.assert_called_once_with(f"cases/{issue.id}")
    assert documents == []
    assert url == None


@pytest.mark.django_db
def test_get_case_folder_info_B(mock_api):
    """Check service function when there is a proper case folder."""
    issue = IssueFactory()
    mock_api.folder.get_children.return_value = [
        {
            "name": "War and Peace",
            "webUrl": "https://en.wikipedia.org/wiki/War_and_Peace",
            "id": "12345",
            "size": 23456,
            "file": {"content_type": "text/html"},
        }
    ]
    mock_api.folder.get.return_value = {
        "webUrl": "https://en.wikipedia.org/wiki/Leo_Tolstoy"
    }

    documents, url = get_case_folder_info(issue)

    mock_api.folder.get_children.assert_called_once_with(f"cases/{issue.id}")
    mock_api.folder.get.assert_called_once_with(f"cases/{issue.id}")
    assert url == "https://en.wikipedia.org/wiki/Leo_Tolstoy"
    assert documents[0] == {
        "name": "War and Peace",
        "url": "https://en.wikipedia.org/wiki/War_and_Peace",
        "id": "12345",
        "size": 23456,
        "is_file": True,
    }


@pytest.mark.django_db
def test_set_up_coordinator_A(mock_api):
    """Check service function doesn't add User who is already a Group member."""
    user = UserFactory()
    mock_api.group.members.return_value = [user.email]

    set_up_coordinator(user)

    mock_api.group.members.assert_called_once()
    mock_api.group.add_user.assert_not_called()


@pytest.mark.django_db
def test_set_up_coordinator_B(mock_api):
    """Check service function adds User who is not already a Group member."""
    user = UserFactory()
    mock_api.group.members.return_value = []

    set_up_coordinator(user)

    mock_api.group.members.assert_called_once()
    mock_api.group.add_user.assert_called_once_with(user.email)


@pytest.mark.django_db
def test_tear_down_coordinator_A(mock_api):
    """Check service function removes User who is already a Group member."""
    user = UserFactory()
    mock_api.group.members.return_value = [user.email]
    mock_api.user.get.return_value = {"id": user.id}

    tear_down_coordinator(user)

    mock_api.group.members.assert_called_once()
    mock_api.user.get.assert_called_once_with(user.email)
    mock_api.group.remove_user.assert_called_once_with(user.id)


@pytest.mark.django_db
def test_tear_down_coordinator_B(mock_api):
    """Check service function doesn't remove User who is not already a Group member."""
    user = UserFactory()
    mock_api.group.members.return_value = []

    tear_down_coordinator(user)

    mock_api.group.members.assert_called_once()
    mock_api.user.get.assert_not_called()
    mock_api.group.remove_user.assert_not_called()
