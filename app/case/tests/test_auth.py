"""
Test authentication
"""
import pytest
from django.urls import reverse

from core.factories import UserFactory


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
