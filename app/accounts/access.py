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


if TYPE_CHECKING:
    from accounts.models import User


class UserAccessEventManagerInterface(Protocol):
    """Abstract interface for user access operations."""

    def user_activated(self, user: User) -> None:
        raise NotImplementedError()

    def user_deactivated(self, user: User) -> None:
        raise NotImplementedError()

    def user_added_to_case(self, user: User, issue: Issue) -> None:
        raise NotImplementedError()

    def user_removed_from_case(self, user: User, issue: Issue) -> None:
        raise NotImplementedError()

    def user_role_changed(self, user: User) -> None:
        raise NotImplementedError()


class UserAccessEventAdapter(UserAccessEventManagerInterface):
    """Default adapter that manages access to case resources when user events occur."""

    def __init__(self):
        # Keep initialisation lightweight; the underlying service modules create
        # API clients lazily.
        from microsoft import service as ms_service

        self._service = ms_service

    def _set_up_licensed_user(self, user: User) -> None:
        created = self._service.set_up_new_user(user)
        if not created:
            # An existing account may have lost its licence on deactivation or
            # demotion. A new account gets one from the ms_account_created task,
            # and assigning it here too would race that task (Graph 409).
            self._service.add_office_licence(user)

    def user_activated(self, user: User) -> None:
        if user.role.is_paralegal_or_better:
            self._set_up_licensed_user(user)

        if user.role.is_coordinator_or_better:
            self._service.add_group_member(user)

    def user_deactivated(self, user: User) -> None:
        self._service.remove_group_member(user)
        self._service.remove_office_licence(user)

    def user_added_to_case(self, user: User, issue: Issue) -> None:
        self._service.add_user_to_case(user, issue)

    def user_removed_from_case(self, user: User, issue: Issue) -> None:
        self._service.remove_user_from_case(user, issue)

    def user_role_changed(self, user: User) -> None:
        if not user.role.is_paralegal_or_better:
            self._service.remove_office_licence(user)
        else:
            self._set_up_licensed_user(user)

        if not user.role.is_coordinator_or_better:
            self._service.remove_group_member(user)
        else:
            self._service.add_group_member(user)
