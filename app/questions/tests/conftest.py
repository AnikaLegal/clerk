from unittest import mock

import pytest
from django.db.models.signals import (m2m_changed, post_delete, post_save, pre_delete,
                                      pre_save)


@pytest.fixture(autouse=True)  # Automatically use in tests.
def disable_signals_fixture(request):
    """
    Pytest fixture for disabling signals

    Re-enable them with
    @pytest.mark.enable_signals

    https://www.cameronmaske.com/muting-django-signals-with-a-pytest-fixture/

    """
    if "enable_signals" in request.keywords:
        return

    signals = [pre_save, post_save, pre_delete, post_delete, m2m_changed]
    restore = {}
    for signal in signals:
        # Temporally remove the signal's receivers (a.k.a attached functions)
        restore[signal] = signal.receivers
        signal.receivers = []

    def restore_signals():
        # When the test tears down, restore the signals.
        for signal, receivers in restore.items():
            signal.receivers = receivers

    # Called after a test has finished.
    request.addfinalizer(restore_signals)
