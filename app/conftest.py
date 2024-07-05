"""
Pytest configuration
"""

import pytest
import os
import debugpy
from django.contrib.auth.models import Group
from rest_framework.test import APIClient
from openapi_tester import SchemaTester

from accounts.models import CaseGroups, User
from utils.signals import disable_signals, restore_signals
from core import factories
from case.middleware import annotate_group_access


schema_tester = SchemaTester(schema_file_path="/app/openapi.generated.yaml")


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


def pytest_sessionstart(session):
    if os.environ.get("DEBUG_PYTEST"):
        debugpy.listen(("0.0.0.0", 8123))
        print("Waiting for debug client to attach...")
        debugpy.wait_for_client()


@pytest.fixture
def user() -> User:
    """
    The base_user is a User model with no permissions assigned
    """
    return factories.UserFactory()


@pytest.fixture
def superuser() -> User:
    return factories.UserFactory(is_superuser=True)


@pytest.fixture
def user_client(user: User) -> APIClient:
    annotate_group_access(user)
    return _login_user(user)


@pytest.fixture
def paralegal_user_client(user: User, paralegal_group) -> APIClient:
    user.groups.set([paralegal_group])
    annotate_group_access(user)
    return _login_user(user)


@pytest.fixture
def superuser_client(superuser: User) -> APIClient:
    annotate_group_access(superuser)
    return _login_user(superuser)


def _login_user(user: User) -> APIClient:
    client = APIClient()
    client.login(username=user.username, password="password")
    client.force_authenticate(user=user)
    return client


@pytest.fixture
def paralegal_group():
    group, _ = Group.objects.get_or_create(name=CaseGroups.PARALEGAL)
    return group


@pytest.fixture
def coordinator_group():
    group, _ = Group.objects.get_or_create(name=CaseGroups.COORDINATOR)
    return group


@pytest.fixture
def admin_group():
    group, _ = Group.objects.get_or_create(name=CaseGroups.ADMIN)
    return group


@pytest.fixture
def lawyer_group():
    group, _ = Group.objects.get_or_create(name=CaseGroups.LAWYER)
    return group
