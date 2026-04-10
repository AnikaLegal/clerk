"""
Factory/registry for obtaining the UserAccessManager instance.

Tests can patch `get_user_access_manager` or call
`set_user_access_manager_for_tests` to inject a test double. The factory will
import the class named by `settings.USER_ACCESS_MANAGER_CLASS` if provided,
otherwise fallback to the default adapter.
"""

from contextlib import contextmanager


from django.conf import settings
from django.utils.module_loading import import_string

from accounts.access import UserAccessEventManagerInterface

_INSTANCE = None


def get_user_event_manager() -> UserAccessEventManagerInterface:
    """
    Return a singleton instance of the configured UserAccessManager.

    If `settings.USER_ACCESS_MANAGER_CLASS` is set (string import path), that
    class will be instantiated. Otherwise the default
    `accounts.access.MicrosoftUserAccessAdapter` is used.
    """
    global _INSTANCE
    if _INSTANCE is not None:
        return _INSTANCE

    cls_path = getattr(settings, "USER_ACCESS_MANAGER_CLASS", None)
    if cls_path:
        cls = import_string(cls_path)
        _INSTANCE = cls()
    else:
        from accounts.access import UserAccessEventAdapter

        _INSTANCE = UserAccessEventAdapter()

    return _INSTANCE


@contextmanager
def override_user_event_manager(instance):
    """
    Context manager to temporarily set the user access manager.

    Restores the previous instance on exit. Useful for tests:

        with override_user_access_manager(mock):
            # run code that triggers handlers

    """
    global _INSTANCE
    prev = _INSTANCE
    _INSTANCE = instance
    try:
        yield
    finally:
        _INSTANCE = prev
