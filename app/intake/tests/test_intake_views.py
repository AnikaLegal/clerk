from datetime import date, timedelta

import pytest

from office.factories import ClosureFactory

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


@pytest.mark.django_db
def test_intake_page_renders_shared_site_chrome(client):
    """
    The intake pages reuse the public website's navbar and footer.
    """
    content = client.get("/intake/").content.decode()
    # Navbar (shared _navbar.html) and footer (shared _footer.html).
    assert "How It Works" in content
    assert "Collections statement" in content


@pytest.mark.django_db
def test_intake_page_hides_get_free_help_cta(client):
    """
    The navbar's "Get free help" call to action is suppressed on the intake
    pages: the visitor is already in the form.
    """
    content = client.get("/intake/").content.decode()
    assert "Get free help</button>" not in content


@pytest.mark.django_db
def test_intake_page_shows_office_closure_notice(client):
    """
    An active office closure is announced on the intake pages as it is on the
    website: the form is where someone most needs to know a reply will wait.
    """
    ClosureFactory(
        template__notice_html="We are closed until {reopen_date}.",
        close_date=date.today() - timedelta(days=1),
        reopen_date=date.today() + timedelta(days=7),
    )
    content = client.get("/intake/").content.decode()
    assert 'id="closure-notice"' in content
    assert "We are closed until" in content


@pytest.mark.django_db
def test_intake_page_without_closure_has_no_notice(client):
    content = client.get("/intake/").content.decode()
    assert 'id="closure-notice"' not in content
