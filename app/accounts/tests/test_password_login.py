"""
Test that password login is refused and Google is the only way in
"""

import pytest
from core.factories import UserFactory
from django.contrib.auth import authenticate
from django.contrib.auth.models import Group, Permission
from django.test import override_settings

PASSWORD = "correct-horse-battery-staple"
GOOGLE_BACKEND = "social_core.backends.google.GoogleOAuth2"


@pytest.fixture
def password_user():
    user = UserFactory(username="admin", is_staff=True, is_superuser=True)
    user.set_password(PASSWORD)
    user.save()
    return user


def is_logged_in(client):
    return "_auth_user_id" in client.session


@pytest.mark.django_db
def test_authenticate_refuses_password(password_user):
    assert authenticate(username="admin", password=PASSWORD) is None


@pytest.mark.django_db
@override_settings(PASSWORD_LOGIN_ENABLED=True)
def test_authenticate_accepts_password_when_enabled(password_user):
    assert authenticate(username="admin", password=PASSWORD) == password_user


@pytest.mark.django_db
@pytest.mark.parametrize("url", ["/accounts/login/", "/admin/login/", "/cms/admin/login/"])
def test_password_login_refused(client, password_user, url):
    client.post(url, {"username": "admin", "password": PASSWORD})
    assert not is_logged_in(client)


@pytest.mark.django_db
def test_admin_login_redirects_to_clerk_login(client):
    resp = client.get("/admin/login/?next=/admin/")
    assert resp.status_code == 302
    assert resp.url == "/accounts/login/?next=%2Fadmin%2F"


@pytest.mark.django_db
def test_admin_login_forbidden_when_signed_in(client):
    # A signed-in user without admin access must not bounce between logins.
    client.force_login(UserFactory(), backend=GOOGLE_BACKEND)
    assert client.get("/admin/login/").status_code == 403


@pytest.mark.django_db
@override_settings(PASSWORD_LOGIN_ENABLED=True)
def test_admin_password_login_when_enabled(client, password_user):
    client.post("/admin/login/", {"username": "admin", "password": PASSWORD})
    assert is_logged_in(client)


@pytest.mark.django_db
def test_google_user_keeps_permissions(client):
    group = Group.objects.create(name="Content editors")
    group.permissions.add(Permission.objects.get(codename="access_admin"))
    user = UserFactory()
    user.groups.add(group)
    client.force_login(user, backend=GOOGLE_BACKEND)

    resp = client.get("/cms/admin/")

    assert resp.status_code == 200
    assert resp.wsgi_request.user.has_perm("wagtailadmin.access_admin")
