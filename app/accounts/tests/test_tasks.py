from unittest.mock import patch

import pytest
from core.factories import UserFactory
from django.test import override_settings

from accounts.models import User
from accounts.tasks import welcome_user_task


@pytest.mark.django_db
@override_settings(CLERK_BASE_URL="https://clerk.example.com")
@patch("accounts.tasks.send_email")
def test_welcome_user_task__links_to_this_environment(mock_send_email):
    user = UserFactory(ms_account_initial_password="initial-password")

    welcome_user_task(user.pk)

    body = mock_send_email.call_args.kwargs["body"]
    assert "https://clerk.example.com/clerk/cases/" in body
    assert "initial-password" in body
    # The initial password is only kept until it has been emailed.
    assert User.objects.get(pk=user.pk).ms_account_initial_password is None
