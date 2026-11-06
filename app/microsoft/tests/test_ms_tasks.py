from unittest.mock import MagicMock, patch

import pytest
import requests
from accounts import events
from accounts.models import User
from core.factories import IssueFactory
from microsoft.tasks import assign_user_licence, reset_ms_access


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


def _http_error(status_code):
    response = MagicMock(status_code=status_code)
    return requests.HTTPError(response=response)


@pytest.mark.django_db
@patch("microsoft.tasks.time.sleep")
def test_ms_tasks__assign_user_licence_retries_conflict(
    mock_sleep, mock_api, paralegal_user
):
    """A 409 from Graph is retried rather than ending the task"""
    mock_api.user.assign_license.side_effect = [_http_error(409), {"id": "x"}]

    assign_user_licence(paralegal_user.pk)

    assert mock_api.user.assign_license.call_count == 2


@pytest.mark.django_db
@patch("microsoft.tasks.time.sleep")
def test_ms_tasks__assign_user_licence_raises_other_errors(
    mock_sleep, mock_api, paralegal_user
):
    """Errors other than 409 end the task on the first attempt"""
    mock_api.user.assign_license.side_effect = _http_error(400)

    assign_user_licence(paralegal_user.pk)

    assert mock_api.user.assign_license.call_count == 1
