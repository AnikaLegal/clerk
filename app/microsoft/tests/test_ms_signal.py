from unittest.mock import MagicMock, patch

import pytest
from accounts.models import User
from core.factories import UserFactory
from microsoft import events
from microsoft.service import (
    set_up_new_user,
)
from microsoft.signals import ms_account_created_user


@pytest.fixture
def mock_api():
    # Mock the MSGraphAPI instance
    with patch("microsoft.service.MSGraphAPI") as mock_msgraph_api:
        mock_instance = mock_msgraph_api.return_value
        mock_instance.is_available.return_value = True
        yield mock_instance


@pytest.mark.django_db
def test_ms_service__set_up_existing_user(mock_api):
    """Test signal is not emitted when user already has MS account"""
    user = UserFactory()
    mock_api.user.get.return_value = {"userPrincipalName": user.email}

    handler = MagicMock()
    events.ms_account_created.connect(handler, sender=User)

    set_up_new_user(user)

    handler.assert_not_called()


@pytest.mark.django_db
def test_ms_signal__set_up_new_user(mock_api):
    """Test signal is emitted when a new MS account is created"""
    user = UserFactory()
    mock_api.user.get.return_value = None
    mock_api.user.create.return_value = user, "open sesame"

    handler = MagicMock()
    events.ms_account_created.connect(handler, sender=User)

    set_up_new_user(user)

    handler.assert_called_once_with(
        signal=events.ms_account_created, sender=User, user=user
    )


@pytest.mark.django_db
def test_ms_signal__assign_user_licence_on_ms_account_created_signal_received(mock_api):
    """Test that when ms_account_created signal is received, assign_license is called"""
    user = UserFactory()
    events.ms_account_created.connect(ms_account_created_user, sender=User)
    events.ms_account_created.send(sender=User, user=user)

    mock_api.user.assign_license.assert_called_once_with(user.email)
