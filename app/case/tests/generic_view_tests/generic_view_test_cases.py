from typing import Callable
from dataclasses import dataclass

from factory.django import DjangoModelFactory

from accounts.models import User
from core.factories import PersonFactory, TenancyFactory


class Action:
    LIST = "LIST"
    RETRIEVE = "RETRIEVE"
    UPDATE = "UPDATE"
    CREATE = "CREATE"
    DELETE = "DELETE"
    ALL = (LIST, RETRIEVE, UPDATE, CREATE, DELETE)


@dataclass
class APIViewTestCase:
    # Creates a model instance
    factory: DjangoModelFactory
    # Name of the API view to test
    base_view_name: str
    # Endpoint actions to test
    actions: list[str]
    # Returns true if user should have read permissions
    test_read_permission: Callable[[User], bool]
    # Returns true if user should have write permissions
    # Note: neither of these check for object-level permissions
    test_write_permissions: Callable[[User], bool]


GENERIC_API_TEST_CASES = [
    APIViewTestCase(
        factory=PersonFactory,
        base_view_name="person-api",
        test_read_permission=lambda user: user.is_paralegal_or_better,
        test_write_permissions=lambda user: user.is_coordinator_or_better,
        actions=Action.ALL,
    ),
    APIViewTestCase(
        factory=TenancyFactory,
        base_view_name="tenancy-api",
        test_read_permission=lambda user: user.is_coordinator_or_better,
        test_write_permissions=lambda user: user.is_coordinator_or_better,
        actions=[Action.RETRIEVE, Action.UPDATE],
    ),
]
