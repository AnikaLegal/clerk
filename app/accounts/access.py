"""
Central UserAccessManager interface and default adapter.

This module defines a small interface (base class) for performing user access
and permission changes and a default adapter that delegates to the
`microsoft.service` functions. Tests can provide their own implementation and
the repository's `registry` exposes a factory for DI.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Protocol

from core.models import Issue

from accounts.models import CaseGroups

if TYPE_CHECKING:
    from django.contrib.auth.models import Group

    from accounts.models import User


class UserAccessEventManagerInterface(Protocol):
    """Abstract interface for user access operations."""

    def user_added_to_case(self, user: User, issue: Issue) -> None:
        raise NotImplementedError()

    def user_removed_from_case(self, user: User, issue: Issue) -> None:
        raise NotImplementedError()

    def user_added_to_group(self, user: User, group: Group) -> None:
        raise NotImplementedError()

    def user_removed_from_group(self, user: User, group: Group) -> None:
        raise NotImplementedError()

    def user_activated(self, user: User) -> None:
        raise NotImplementedError()

    def user_deactivated(self, user: User) -> None:
        raise NotImplementedError()


class UserAccessEventAdapter(UserAccessEventManagerInterface):
    """Default adapter that manages access to case resources when user events occur."""

    def __init__(self):
        # Keep initialisation lightweight; the underlying service modules create
        # API clients lazily.
        from microsoft import service as ms_service

        self._service = ms_service

    def user_added_to_case(self, user: User, issue: Issue) -> None:
        self._service.add_user_to_case(user, issue)

    def user_removed_from_case(self, user: User, issue: Issue) -> None:
        self._service.remove_user_from_case(user, issue)

    def user_added_to_group(self, user: User, group: Group) -> None:
        if group.name == CaseGroups.COORDINATOR or group.name == CaseGroups.ADMIN:
            self._service.add_group_member(user)

    def user_removed_from_group(self, user: User, group: Group) -> None:
        # Remove the users group membership when they no longer have coordinator
        # or admin roles.
        if (
            group.name == CaseGroups.COORDINATOR or group.name == CaseGroups.ADMIN
        ) and not user.role.is_coordinator_or_better:
            self._service.remove_group_member(user)

    def user_activated(self, user: User) -> None:
        self._service.add_office_licence(user)
        if user.role.is_coordinator_or_better:
            self._service.add_group_member(user)

    def user_deactivated(self, user: User) -> None:
        if user.role.is_coordinator_or_better:
            self._service.remove_group_member(user)
        self._service.remove_office_licence(user)
