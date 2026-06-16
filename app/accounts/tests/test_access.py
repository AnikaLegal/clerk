from unittest.mock import patch

import pytest
from accounts.access import UserAccessEventAdapter
from core.factories import IssueFactory

# Fixtures


@pytest.fixture()
def mock_ms_service():
    with patch("microsoft.service") as mock_ms_service:
        yield mock_ms_service


# Test that the MicrosoftUserAccessEventAdapter correctly delegates to microsoft.service


@pytest.mark.django_db
def test_microsoft_adapter_case_delegation(mock_ms_service, user):
    issue = IssueFactory()
    adapter = UserAccessEventAdapter()

    adapter.user_added_to_case(user, issue)
    mock_ms_service.add_user_to_case.assert_called_once_with(user, issue)

    adapter.user_removed_from_case(user, issue)
    mock_ms_service.remove_user_from_case.assert_called_once_with(user, issue)


# User activation/deactivation tests


@pytest.mark.django_db
@pytest.mark.parametrize(
    "user_type, is_ms_account_set_up, is_added_to_group",
    [
        ("user", False, False),
        ("paralegal_user", True, False),
        ("lawyer_user", True, False),
        ("coordinator_user", True, True),
        ("admin_user", True, True),
    ],
)
def test_microsoft_adapter_user_activation(
    mock_ms_service, user_type, is_ms_account_set_up, is_added_to_group, request
):
    user = request.getfixturevalue(user_type)
    adapter = UserAccessEventAdapter()

    adapter.user_activated(user)
    if is_ms_account_set_up:
        mock_ms_service.set_up_new_user.assert_called_once_with(user)
        mock_ms_service.add_office_licence.assert_called_once_with(user)
    else:
        mock_ms_service.set_up_new_user.assert_not_called()
        mock_ms_service.add_office_licence.assert_not_called()

    if is_added_to_group:
        mock_ms_service.add_group_member.assert_called_once_with(user)
    else:
        mock_ms_service.add_group_member.assert_not_called()


@pytest.mark.django_db
@pytest.mark.parametrize(
    "user_type",
    [
        "paralegal_user",
        "lawyer_user",
        "coordinator_user",
        "admin_user",
    ],
)
def test_microsoft_adapter_user_deactivation(mock_ms_service, user_type, request):
    user = request.getfixturevalue(user_type)
    adapter = UserAccessEventAdapter()

    adapter.user_deactivated(user)
    mock_ms_service.remove_office_licence.assert_called_with(user)
    mock_ms_service.remove_group_member.assert_called_once_with(user)


# Add Role change tests


@pytest.mark.django_db
@pytest.mark.parametrize(
    "user_type, is_ms_account_set_up, is_added_to_group",
    [
        ("user", False, False),
        ("paralegal_user", True, False),
        ("lawyer_user", True, False),
        ("coordinator_user", True, True),
        ("admin_user", True, True),
    ],
)
def test_microsoft_adapter_user_role_change(
    mock_ms_service, user_type, is_ms_account_set_up, is_added_to_group, request
):
    user = request.getfixturevalue(user_type)
    adapter = UserAccessEventAdapter()
    adapter.user_role_changed(user)

    if is_ms_account_set_up:
        mock_ms_service.set_up_new_user.assert_called_once_with(user)
        mock_ms_service.add_office_licence.assert_called_once_with(user)
        mock_ms_service.remove_office_licence.assert_not_called()
    else:
        mock_ms_service.remove_office_licence.assert_called_once_with(user)
        mock_ms_service.set_up_new_user.assert_not_called()
        mock_ms_service.add_office_licence.assert_not_called()

    if is_added_to_group:
        mock_ms_service.add_group_member.assert_called_once_with(user)
        mock_ms_service.remove_group_member.assert_not_called()
    else:
        mock_ms_service.remove_group_member.assert_called_once_with(user)
        mock_ms_service.add_group_member.assert_not_called()
