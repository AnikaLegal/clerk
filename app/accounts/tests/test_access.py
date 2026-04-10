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
    "user_type, is_added_to_group",
    [
        ("paralegal_user", False),
        ("lawyer_user", False),
        ("coordinator_user", True),
        ("admin_user", True),
    ],
)
def test_microsoft_adapter_user_activation(
    mock_ms_service, user_type, is_added_to_group, request
):
    user = request.getfixturevalue(user_type)
    adapter = UserAccessEventAdapter()

    adapter.user_activated(user)
    mock_ms_service.add_office_licence.assert_called_with(user)

    if is_added_to_group:
        mock_ms_service.add_group_member.assert_called_once_with(user)
    else:
        mock_ms_service.add_group_member.assert_not_called()


@pytest.mark.django_db
@pytest.mark.parametrize(
    "user_type, is_removed_from_group",
    [
        ("paralegal_user", False),
        ("lawyer_user", False),
        ("coordinator_user", True),
        ("admin_user", True),
    ],
)
def test_microsoft_adapter_user_deactivation(
    mock_ms_service, user_type, is_removed_from_group, request
):
    user = request.getfixturevalue(user_type)
    adapter = UserAccessEventAdapter()

    adapter.user_deactivated(user)
    mock_ms_service.remove_office_licence.assert_called_with(user)
    if is_removed_from_group:
        mock_ms_service.remove_group_member.assert_called_once_with(user)
    else:
        mock_ms_service.remove_group_member.assert_not_called()


# Add group membership tests


@pytest.mark.django_db
def test_microsoft_adapter_paralegal_group_does_not_trigger_add(
    mock_ms_service, user, paralegal_group
):
    adapter = UserAccessEventAdapter()

    adapter.user_added_to_group(user, paralegal_group)
    mock_ms_service.add_group_member.assert_not_called()


@pytest.mark.django_db
def test_microsoft_adapter_lawyer_group_does_not_trigger_add(
    mock_ms_service, user, lawyer_group
):
    adapter = UserAccessEventAdapter()

    adapter.user_added_to_group(user, lawyer_group)
    mock_ms_service.add_group_member.assert_not_called()


@pytest.mark.django_db
def test_microsoft_adapter_coordinator_group_triggers_add(
    mock_ms_service, user, admin_group
):
    adapter = UserAccessEventAdapter()

    adapter.user_added_to_group(user, admin_group)
    mock_ms_service.add_group_member.assert_called_once_with(user)


@pytest.mark.django_db
def test_microsoft_adapter_admin_group_triggers_add(mock_ms_service, user, admin_group):
    adapter = UserAccessEventAdapter()
    adapter.user_added_to_group(user, admin_group)
    mock_ms_service.add_group_member.assert_called_once_with(user)


# Remove group membership tests


@pytest.mark.django_db
def test_microsoft_adapter_remove_paralegal_group_member(
    mock_ms_service, user, paralegal_group
):
    adapter = UserAccessEventAdapter()
    adapter.user_removed_from_group(user, paralegal_group)
    mock_ms_service.remove_group_member.assert_not_called()


@pytest.mark.django_db
def test_microsoft_adapter_remove_lawyer_group_member(
    mock_ms_service, user, lawyer_group
):
    adapter = UserAccessEventAdapter()
    adapter.user_removed_from_group(user, lawyer_group)
    mock_ms_service.remove_group_member.assert_not_called()


@pytest.mark.django_db
def test_microsoft_adapter_remove_coordinator_group_member(
    mock_ms_service, user, coordinator_group
):
    adapter = UserAccessEventAdapter()
    adapter.user_removed_from_group(user, coordinator_group)
    mock_ms_service.remove_group_member.assert_called_once_with(user)


@pytest.mark.django_db
def test_microsoft_adapter_remove_admin_group_member(
    mock_ms_service, user, admin_group
):
    adapter = UserAccessEventAdapter()
    adapter.user_removed_from_group(user, admin_group)
    mock_ms_service.remove_group_member.assert_called_once_with(user)


@pytest.mark.django_db
def test_microsoft_adapter_remove_group_member_not_called_when_still_admin(
    mock_ms_service, admin_user, coordinator_group
):
    adapter = UserAccessEventAdapter()
    adapter.user_removed_from_group(admin_user, coordinator_group)
    mock_ms_service.remove_group_member.assert_not_called()


@pytest.mark.django_db
def test_microsoft_adapter_remove_group_member_not_called_when_still_coordinator(
    mock_ms_service, coordinator_user, admin_group
):
    adapter = UserAccessEventAdapter()
    adapter.user_removed_from_group(coordinator_user, admin_group)
    mock_ms_service.remove_group_member.assert_not_called()
