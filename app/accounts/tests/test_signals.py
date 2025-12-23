from unittest.mock import MagicMock, patch

import pytest
from core.factories import IssueFactory, UserFactory
from django.contrib.auth.models import Group
from utils.signals import DisableSignals

from accounts import registry
from accounts.models import CaseGroups

# Fixtures


@pytest.fixture()
def mock_user_event_mgr():
    mock_mgr = MagicMock()
    with registry.override_user_event_manager(mock_mgr):
        yield mock_mgr


# Test that signals correctly call the UserAccessEventManager methods

# Test cases for user activation/deactivation


@pytest.mark.enable_signals
@pytest.mark.django_db
def test_new_inactive_user(mock_user_event_mgr):
    UserFactory(is_active=False)
    mock_user_event_mgr.user_activated.assert_not_called()
    mock_user_event_mgr.user_deactivated.assert_not_called()


@pytest.mark.enable_signals
@pytest.mark.django_db
def test_new_active_user(mock_user_event_mgr):
    user = UserFactory(is_active=True)
    mock_user_event_mgr.user_activated.assert_called_once_with(user)
    mock_user_event_mgr.user_deactivated.assert_not_called()


@pytest.mark.enable_signals
@pytest.mark.django_db
def test_activate_existing_inactive_user(mock_user_event_mgr):
    user = UserFactory(is_active=False)
    user.is_active = True
    user.save()
    mock_user_event_mgr.user_activated.assert_called_once_with(user)
    mock_user_event_mgr.user_deactivated.assert_not_called()


@pytest.mark.enable_signals
@pytest.mark.django_db
def test_deactivate_existing_active_user(mock_user_event_mgr):
    with DisableSignals():
        user = UserFactory(is_active=True)

    user.is_active = False
    user.save()
    mock_user_event_mgr.user_activated.assert_not_called()
    mock_user_event_mgr.user_deactivated.assert_called_once_with(user)


@pytest.mark.enable_signals
@pytest.mark.django_db
def test_delete_inactive_user(mock_user_event_mgr):
    user = UserFactory(is_active=False)
    user.delete()
    mock_user_event_mgr.user_activated.assert_not_called()
    mock_user_event_mgr.user_deactivated.assert_not_called()


@pytest.mark.enable_signals
@pytest.mark.django_db
def test_delete_active_user(mock_user_event_mgr):
    with DisableSignals():
        user = UserFactory(is_active=True)
    user.delete()

    mock_user_event_mgr.user_activated.assert_not_called()
    mock_user_event_mgr.user_deactivated.assert_called_once_with(user)


# Test cases for adding/removing groups


@pytest.mark.enable_signals
@pytest.mark.django_db
@pytest.mark.parametrize("group_name", CaseGroups.values)
def test_add_group(mock_user_event_mgr, group_name, user):
    group = Group.objects.get(name=group_name)

    user.groups.add(group)
    mock_user_event_mgr.user_added_to_group.assert_called_once_with(user, group)


@pytest.mark.enable_signals
@pytest.mark.django_db
@pytest.mark.parametrize("group_name", CaseGroups.values)
def test_remove_group(mock_user_event_mgr, group_name, user):
    group = Group.objects.get(name=group_name)
    user.groups.add(group)

    user.groups.remove(group)
    mock_user_event_mgr.user_removed_from_group.assert_called_once_with(user, group)


@pytest.mark.enable_signals
@pytest.mark.django_db
def test_remove_paralegal_from_group(
    mock_user_event_mgr, paralegal_user, paralegal_group
):
    IssueFactory(is_case_sent=True, paralegal=paralegal_user)
    paralegal_user.groups.remove(paralegal_group)
    # NOTE: removing paralegal from group does NOT remove from case.
    mock_user_event_mgr.user_removed_from_case.assert_not_called()


@pytest.mark.enable_signals
@pytest.mark.django_db
def test_remove_lawyer_from_group(mock_user_event_mgr, lawyer_user, lawyer_group):
    IssueFactory(is_case_sent=True, lawyer=lawyer_user)
    lawyer_user.groups.remove(lawyer_group)
    # NOTE: removing lawyer from group does NOT remove from case.
    mock_user_event_mgr.user_removed_from_case.assert_not_called()


# Test cases for adding/removing users to/from cases


@pytest.mark.enable_signals
@pytest.mark.django_db
@patch("core.signals.issue_event.send_case_assignment_slack")
def test_add_paralegal_to_case(
    mock_send_case_assignment_slack, mock_user_event_mgr, paralegal_user
):
    issue = IssueFactory(is_case_sent=True, paralegal=None)
    issue.paralegal = paralegal_user
    issue.save()

    mock_user_event_mgr.user_added_to_case.assert_called_once_with(
        paralegal_user, issue
    )


@pytest.mark.enable_signals
@pytest.mark.django_db
def test_remove_paralegal_from_case(mock_user_event_mgr, paralegal_user):
    issue = IssueFactory(is_case_sent=True, paralegal=paralegal_user)
    issue.paralegal = None
    issue.save()

    mock_user_event_mgr.user_removed_from_case.assert_called_once_with(
        paralegal_user, issue
    )


@pytest.mark.enable_signals
@pytest.mark.django_db
def test_add_lawyer_to_case(mock_user_event_mgr, lawyer_user):
    issue = IssueFactory(is_case_sent=True, paralegal=None)
    issue.lawyer = lawyer_user
    issue.save()

    mock_user_event_mgr.user_added_to_case.assert_called_once_with(lawyer_user, issue)


@pytest.mark.enable_signals
@pytest.mark.django_db
def test_remove_lawyer_from_case(mock_user_event_mgr, lawyer_user):
    issue = IssueFactory(is_case_sent=True, lawyer=lawyer_user)
    issue.lawyer = None
    issue.save()

    mock_user_event_mgr.user_removed_from_case.assert_called_once_with(
        lawyer_user, issue
    )
