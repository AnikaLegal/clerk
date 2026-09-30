from unittest.mock import MagicMock, patch

import pytest
from accounts import events
from accounts.models import User
from core.factories import IssueFactory
from microsoft.tasks import reset_ms_access


@pytest.fixture
def mock_api():
    # Mock the MSGraphAPI instance
    with patch("microsoft.service.MSGraphAPI") as mock_msgraph_api:
        mock_instance = mock_msgraph_api.return_value
        mock_instance.is_available.return_value = True
        yield mock_instance


@pytest.mark.django_db
def test_ms_tasks__reset_ms_access_sends_role_changed(mock_api, coordinator_user):
    """Test the user's role event is re-sent when their access is reset"""
    mock_api.user.get.return_value = {"userPrincipalName": coordinator_user.email}

    handler = MagicMock()
    events.user_role_changed.connect(handler, sender=User)

    reset_ms_access(coordinator_user)

    handler.assert_called_once_with(
        signal=events.user_role_changed, sender=User, user=coordinator_user
    )


@pytest.mark.django_db
def test_ms_tasks__reset_ms_access_sends_added_to_case(mock_api, paralegal_user):
    """Test the user's case access events are re-sent when their access is reset"""
    mock_api.user.get.return_value = {"userPrincipalName": paralegal_user.email}
    issue = IssueFactory(paralegal=paralegal_user)

    handler = MagicMock()
    events.user_added_to_case.connect(handler, sender=User)

    reset_ms_access(paralegal_user)

    handler.assert_called_once_with(
        signal=events.user_added_to_case,
        sender=User,
        user=paralegal_user,
        issue=issue,
    )
