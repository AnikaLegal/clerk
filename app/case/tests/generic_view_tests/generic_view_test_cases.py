from typing import Callable
from dataclasses import dataclass

from factory.django import DjangoModelFactory

from accounts.models import User
from core.factories import PersonFactory


@dataclass
class APIViewTestCase:
    factory: DjangoModelFactory
    base_view_name: str
    test_read_permission: Callable[[User], bool]
    test_write_permissions: Callable[[User], bool]


GENERIC_API_TEST_CASES = [
    APIViewTestCase(
        factory=PersonFactory,
        base_view_name="person-api",
        test_read_permission=lambda user: user.is_paralegal_or_better,
        test_write_permissions=lambda user: user.is_coordinator_or_better,
    )
]
