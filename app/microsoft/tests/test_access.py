"""
High level tests of business logic to do with granting/revoking access to Sharepoint.
"""
from unittest.mock import patch

import pytest
from django.contrib.auth.models import Group

from accounts.models import CaseGroups
from core.factories import UserFactory, IssueFactory


@pytest.mark.enable_signals
@pytest.mark.django_db
@patch("accounts.signals.remove_user_from_case")
@patch("accounts.signals.set_up_coordinator")
@patch("accounts.signals.tear_down_coordinator")
def test_add_coordinator(
    tear_down_coordinator, set_up_coordinator, remove_user_from_case
):
    user = UserFactory()
    group = Group.objects.get(name=CaseGroups.COORDINATOR)
    set_up_coordinator.assert_not_called()
    user.groups.add(group)
    set_up_coordinator.assert_called_once_with(user)


@pytest.mark.enable_signals
@pytest.mark.django_db
@patch("accounts.signals.remove_user_from_case")
@patch("accounts.signals.set_up_coordinator")
@patch("accounts.signals.tear_down_coordinator")
def test_remove_coordinator(
    tear_down_coordinator, set_up_coordinator, remove_user_from_case
):
    user = UserFactory()
    group = Group.objects.get(name=CaseGroups.COORDINATOR)
    user.groups.add(group)
    tear_down_coordinator.assert_not_called()
    user.groups.remove(group)
    tear_down_coordinator.assert_called_once_with(user)


@pytest.mark.enable_signals
@pytest.mark.django_db
@patch("accounts.signals.remove_user_from_case")
@patch("accounts.signals.set_up_coordinator")
@patch("accounts.signals.tear_down_coordinator")
def test_add_admin(tear_down_coordinator, set_up_coordinator, remove_user_from_case):
    user = UserFactory()
    group = Group.objects.get(name=CaseGroups.ADMIN)
    set_up_coordinator.assert_not_called()
    user.groups.add(group)
    set_up_coordinator.assert_called_once_with(user)


@pytest.mark.enable_signals
@pytest.mark.django_db
@patch("accounts.signals.remove_user_from_case")
@patch("accounts.signals.set_up_coordinator")
@patch("accounts.signals.tear_down_coordinator")
def test_remove_admin(tear_down_coordinator, set_up_coordinator, remove_user_from_case):
    user = UserFactory()
    group = Group.objects.get(name=CaseGroups.ADMIN)
    user.groups.add(group)
    tear_down_coordinator.assert_not_called()
    user.groups.remove(group)
    tear_down_coordinator.assert_called_once_with(user)


@pytest.mark.enable_signals
@pytest.mark.django_db
@patch("accounts.signals.remove_user_from_case")
@patch("accounts.signals.set_up_coordinator")
@patch("accounts.signals.tear_down_coordinator")
def test_admin_to_coordinator(
    tear_down_coordinator, set_up_coordinator, remove_user_from_case
):
    user = UserFactory()
    admin_group = Group.objects.get(name=CaseGroups.ADMIN)
    coordinator_group = Group.objects.get(name=CaseGroups.COORDINATOR)
    user.groups.add(admin_group)
    user.groups.add(coordinator_group)
    tear_down_coordinator.assert_not_called()
    user.groups.remove(admin_group)
    tear_down_coordinator.assert_not_called()


@pytest.mark.enable_signals
@pytest.mark.django_db
@patch("core.signals.issue.remove_user_from_case")
@patch("core.signals.issue.add_user_to_case")
def test_add_paralegal_to_case(add_user_to_case, remove_user_from_case):
    user = UserFactory()
    issue = IssueFactory(is_case_sent=True, paralegal=None)
    add_user_to_case.assert_not_called()
    issue.paralegal = user
    issue.lawyer = UserFactory()
    issue.save()
    add_user_to_case.assert_called_once_with(user, issue)


@pytest.mark.enable_signals
@pytest.mark.django_db
@patch("core.signals.issue.remove_user_from_case")
@patch("core.signals.issue.add_user_to_case")
def test_remove_paralegal_from_case(add_user_to_case, remove_user_from_case):
    user = UserFactory()
    issue = IssueFactory(is_case_sent=True, paralegal=user, lawyer=UserFactory())
    remove_user_from_case.assert_not_called()
    issue.paralegal = UserFactory()
    issue.save()
    remove_user_from_case.assert_called_once_with(user, issue)


@pytest.mark.enable_signals
@pytest.mark.django_db
@patch("accounts.signals.remove_user_from_case")
@patch("accounts.signals.set_up_coordinator")
@patch("accounts.signals.tear_down_coordinator")
@patch("core.signals.issue.remove_user_from_case")
@patch("core.signals.issue.add_user_to_case")
def test_remove_paralegal_from_group(
    core_add_user_to_case,
    core_remove_user_from_case,
    accounts_tear_down_coordinator,
    accounts_set_up_coordinator,
    accounts_remove_user_from_case,
):
    user = UserFactory()
    group = Group.objects.get(name=CaseGroups.PARALEGAL)
    user.groups.add(group)
    issue = IssueFactory(is_case_sent=True, paralegal=user)

    accounts_remove_user_from_case.assert_not_called()
    user.groups.remove(group)
    accounts_remove_user_from_case.assert_called_once_with(user, issue)
