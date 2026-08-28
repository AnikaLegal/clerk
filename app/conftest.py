"""
Pytest configuration
"""

import os
from enum import Enum

import debugpy
import factory
import pytest
from accounts.models import CaseGroups, User
from case.middleware import annotate_group_access
from core import factories
from django.contrib.auth.models import Group
from django.core.cache import cache
from openapi_tester import SchemaTester
from openapi_tester.clients import OpenAPIClient
from utils.signals import disable_signals, restore_signals
from zeal import zeal_context

schema_tester = SchemaTester(schema_file_path="/app/openapi.generated.yaml")


class CaseRole(Enum):
    NONE = 1
    PARALEGAL = 2
    LAWYER = 3


@pytest.fixture(autouse=True, scope="session")
def set_faker_locale():
    with factory.Faker.override_default_locale("en_AU"):
        yield


@pytest.fixture(autouse=True, scope="function")
def use_zeal():
    with zeal_context():
        yield


@pytest.fixture(autouse=True)
def reset_throttles():
    """
    DRF counts throttled requests in the cache, which outlives a test - without
    this, tests hitting a throttled endpoint would start failing based on what
    ran before them.
    """
    cache.clear()
    yield
    cache.clear()


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
    if os.environ.get("DEBUGPY"):
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
def unprivileged_user(user) -> User:
    annotate_group_access(user)
    return user


@pytest.fixture
def paralegal_user(user, paralegal_group) -> User:
    user.groups.set([paralegal_group])
    annotate_group_access(user)
    return user


@pytest.fixture
def lawyer_user(user, lawyer_group) -> User:
    user.groups.set([lawyer_group])
    annotate_group_access(user)
    return user


@pytest.fixture
def coordinator_user(user, coordinator_group) -> User:
    user.groups.set([coordinator_group])
    annotate_group_access(user)
    return user


@pytest.fixture
def admin_user(user, admin_group) -> User:
    user.groups.set([admin_group])
    annotate_group_access(user)
    return user


@pytest.fixture
def superuser() -> User:
    user = factories.UserFactory(is_superuser=True)
    annotate_group_access(user)
    return user


@pytest.fixture
def paralegal_group():
    group, _ = Group.objects.get_or_create(name=CaseGroups.PARALEGAL)
    return group


@pytest.fixture
def lawyer_group():
    group, _ = Group.objects.get_or_create(name=CaseGroups.LAWYER)
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
def anon_client() -> OpenAPIClient:
    """
    Anonymous client for the public intake API, with responses validated
    against the OpenAPI schema.
    """
    return OpenAPIClient(schema_tester=schema_tester)


@pytest.fixture
def user_client(unprivileged_user) -> OpenAPIClient:
    return _login_user(unprivileged_user)


@pytest.fixture
def paralegal_user_client(paralegal_user) -> OpenAPIClient:
    return _login_user(paralegal_user)


@pytest.fixture
def lawyer_user_client(lawyer_user) -> OpenAPIClient:
    return _login_user(lawyer_user)


@pytest.fixture
def coordinator_user_client(coordinator_user) -> OpenAPIClient:
    return _login_user(coordinator_user)


@pytest.fixture
def admin_user_client(admin_user) -> OpenAPIClient:
    return _login_user(admin_user)


@pytest.fixture
def superuser_client(superuser: User) -> OpenAPIClient:
    return _login_user(superuser)


def _login_user(user: User) -> OpenAPIClient:
    client = OpenAPIClient(schema_tester=schema_tester)
    client.force_login(user=user)
    client.force_authenticate(user=user)
    return client
