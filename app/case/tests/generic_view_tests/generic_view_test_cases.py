from collections.abc import Callable
from dataclasses import dataclass

from factory.django import DjangoModelFactory

from accounts.models import User
from caller.factories import CallbackFactory, CallFactory
from core.factories import (
    EmailTemplateFactory,
    NotificationFactory,
    UserFactory,
)
from webhooks.factories import WebflowContactFactory


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
    test_read_permissions: Callable[[User], bool]
    # Returns true if user should have write permissions
    test_write_permissions: Callable[[User], bool]
    # Note: neither of these flags check for object-level permissions


GENERIC_API_TEST_CASES = [
    APIViewTestCase(
        factory=UserFactory,
        base_view_name="account-api",
        test_read_permissions=lambda user: user.is_coordinator_or_better,
        test_write_permissions=lambda user: user.is_coordinator_or_better,
        actions=[Action.LIST, Action.UPDATE],  # Create tested elsewhere.
    ),
    APIViewTestCase(
        factory=EmailTemplateFactory,
        base_view_name="template-email-api",
        test_read_permissions=lambda user: user.is_admin_or_better,
        test_write_permissions=lambda user: user.is_admin_or_better,
        actions=Action.ALL,
    ),
    APIViewTestCase(
        factory=NotificationFactory,
        base_view_name="template-notify-api",
        test_read_permissions=lambda user: user.is_admin_or_better,
        test_write_permissions=lambda user: user.is_admin_or_better,
        actions=Action.ALL,
    ),
    APIViewTestCase(
        factory=CallFactory,
        base_view_name="call-api",
        test_read_permissions=lambda user: user.is_coordinator_or_better,
        test_write_permissions=lambda user: user.is_coordinator_or_better,
        actions=[Action.LIST, Action.UPDATE],
    ),
    APIViewTestCase(
        factory=WebflowContactFactory,
        base_view_name="contact-api",
        test_read_permissions=lambda user: user.is_coordinator_or_better,
        test_write_permissions=lambda user: user.is_coordinator_or_better,
        actions=[Action.LIST, Action.UPDATE],
    ),
    APIViewTestCase(
        factory=CallbackFactory,
        base_view_name="callback-api",
        test_read_permissions=lambda user: user.is_coordinator_or_better,
        test_write_permissions=lambda user: user.is_coordinator_or_better,
        actions=[Action.CREATE],  # Listing needs a filter, tested elsewhere.
    ),
]
