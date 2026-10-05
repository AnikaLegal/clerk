import pytest
from django.contrib.auth.models import AnonymousUser
from django.test import Client, RequestFactory

from accounts.models import User
from case.utils import render_react_page


def test_render_react_page_defaults_role_flags_for_anonymous_user():
    request = RequestFactory().get("/clerk/")
    request.user = AnonymousUser()

    response = render_react_page(request, "Not Found", "404", {}, status=404)

    assert response.status_code == 404


@pytest.mark.django_db
def test_unknown_clerk_path_redirects_anonymous_user_to_login(client: Client):
    response = client.get("/clerk/this/path/does/not/exist/")

    assert response.status_code == 302
    assert "next=/clerk/this/path/does/not/exist/" in response["Location"]


@pytest.mark.django_db
def test_unknown_clerk_path_redirects_anonymous_user_to_login_in_debug(
    client: Client, settings
):
    settings.DEBUG = True

    response = client.get("/clerk/this/path/does/not/exist/")

    assert response.status_code == 302
    assert "next=/clerk/this/path/does/not/exist/" in response["Location"]


@pytest.mark.django_db
def test_unknown_clerk_api_path_is_not_redirected_for_anonymous_user(client: Client):
    response = client.get("/clerk/api/this/path/does/not/exist/")

    assert response.status_code == 404


@pytest.mark.django_db
def test_unknown_clerk_path_renders_404_page_for_authenticated_user(
    client: Client, user: User
):
    client.force_login(user)

    response = client.get("/clerk/this/path/does/not/exist/")

    assert response.status_code == 404
    assert b"REACT_CONTEXT" in response.content
