import pytest

INTAKE_PATHS = [
    "/intake/",
    "/intake/form/",
    "/intake/resume/",
    "/intake/submitted/",
    "/intake/abandon/",
    "/intake/no-email/",
    "/intake/means/",
    "/intake/geography/",
    "/intake/bonds-recovery/",
]


@pytest.mark.django_db
@pytest.mark.parametrize("path", INTAKE_PATHS)
def test_intake_page_loads_anonymously(client, path):
    """
    The intake single page app is served on all its client side routes
    without authentication.
    """
    response = client.get(path)
    assert response.status_code == 200


@pytest.mark.django_db
def test_intake_page_sets_csrf_cookie(client):
    """
    The intake page sets a CSRF cookie so logged-in staff can POST to the
    submission API (SessionAuthentication enforces CSRF for them).
    """
    response = client.get("/intake/")
    assert "csrftoken" in response.cookies


@pytest.mark.django_db
def test_intake_page_supports_head(client):
    """
    Uptime monitors and crawlers issue HEAD requests to public pages.
    """
    response = client.head("/intake/")
    assert response.status_code == 200


@pytest.mark.django_db
def test_intake_page_rejects_post(client):
    response = client.post("/intake/")
    assert response.status_code == 405
