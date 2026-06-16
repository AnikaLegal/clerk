"""
Utils for disabling and re-enabling signals.
https://www.cameronmaske.com/muting-django-signals-with-a-pytest-fixture/
"""

from accounts.events import (
    user_activated,
    user_added_to_case,
    user_deactivated,
    user_removed_from_case,
    user_role_changed,
)
from django.db.models.signals import (
    m2m_changed,
    post_delete,
    post_save,
    pre_delete,
    pre_save,
)
from microsoft.events import ms_account_created

SIGNALS = [
    pre_save,
    post_save,
    pre_delete,
    post_delete,
    m2m_changed,
    user_activated,
    user_deactivated,
    user_added_to_case,
    user_removed_from_case,
    user_role_changed,
    ms_account_created,
]
RESTORE = {}


def disable_signals():
    """
    Temporally remove the signal's receivers (a.k.a attached functions)
    """
    for signal in SIGNALS:
        RESTORE[signal] = signal.receivers
        signal.receivers = []


def restore_signals():
    """
    When the test tears down, restore the signals.
    """
    signals = list(RESTORE.keys())
    for signal in signals:
        signal.sender_receivers_cache.clear()
        signal.receivers = RESTORE[signal]
        del RESTORE[signal]


class DisableSignals:
    def __init__(self):
        self.restore = {}

    def __enter__(self):
        for signal in SIGNALS:
            self.restore[signal] = signal.receivers
            signal.receivers = []

    def __exit__(self, type, value, traceback):
        for signal in self.restore.keys():
            signal.receivers = self.restore[signal]
