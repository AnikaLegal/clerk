"""
Smoke tests for URLS
"""
import pytest

URLS_TO_TEST = [
    # url, status code expected, redirect url expected
    # FIXME: Figure out how to do this with new website
    # ("/", 302, "/cases/"),
    # ("/login/", 200, None),
    # ("/robots.txt", 200, None),
]


@pytest.mark.django_db
@pytest.mark.parametrize("url, status_code, redirect_url", URLS_TO_TEST)
def test_url_status_codes(client, url, status_code, redirect_url):
    """
    Ensure URLs return the correct status code.
    """
    response = client.get(url)

    # Check basic status.
    msg = f"URL {url} failed, expecting {status_code} got {response.status_code}"
    assert response.status_code == status_code, msg
    # Check redirects.
    if response.status_code in [301, 302]:
        response_redirect = client.get(url, follow=True)
        # Ensure single redirect only
        msg = f"Multiple redirects for {url}\n{response_redirect.redirect_chain}"
        assert len(response_redirect.redirect_chain) == 1, msg
        # Ensure lands on expected URL
        actual_redirect_url = response_redirect.redirect_chain[0][0]
        msg = (
            f"Wrong redirect for {url} expected {redirect_url}, got {actual_redirect_url}"
        )
        assert actual_redirect_url == redirect_url, msg
