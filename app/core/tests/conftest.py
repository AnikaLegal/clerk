from unittest import mock

import pytest

from utils.signals import disable_signals, restore_signals


@pytest.fixture(autouse=True)  # Automatically use in tests.
def disable_signals_fixture(request):
    """
    Pytest fixture for disabling signals

    Re-enable them with
    @pytest.mark.enable_signals


    """
    if "enable_signals" in request.keywords:
        return

    disable_signals()
    # Called after a test has finished.
    request.addfinalizer(restore_signals)


def pytest_configure(config):
    """
    Register restore signals mark
    """
    config.addinivalue_line("markers", "enable_signals: Mark test to use signals.")
