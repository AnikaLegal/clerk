"""
Test authentication
"""

import pytest
from core.factories import UserFactory
from django.contrib.messages import get_messages
from django.urls import reverse
from social_core.backends.google import GoogleOAuth2
from social_django.utils import load_strategy


@pytest.mark.django_db
def test_logout(client):
    """
    Ensure URLs return the correct status code.
    """
    user = UserFactory()
    client.force_login(user)
    assert user.is_authenticated
    resp = client.get(reverse("logout"))
    # Redirects back to login page
    assert resp.status_code == 302
    assert resp.url == reverse("login")
    # Sets session ID to empty string
    resp.cookies["sessionid"].value == ""


@pytest.mark.parametrize(
    "email, allowed",
    [
        ("jane.doe@anikalegal.org.au", True),
        ("Jane.Doe@AnikaLegal.org.au", True),
        ("jane.doe@anikalegal.com", False),
        ("jane.doe@gmail.com", False),
    ],
)
def test_google_login_allowed_domains(email, allowed):
    backend = GoogleOAuth2(load_strategy())
    assert backend.auth_allowed(response={}, details={"email": email}) is allowed


@pytest.mark.django_db
def test_google_callback_without_session_state_redirects_to_login(client):
    resp = client.get(
        reverse("social:complete", args=["google-oauth2"]),
        {"state": "stale", "code": "code"},
    )
    assert resp.status_code == 302
    assert resp.url == reverse("login")
    assert [str(m) for m in get_messages(resp.wsgi_request)] == [
        "Your login session expired. Please log in again."
    ]
