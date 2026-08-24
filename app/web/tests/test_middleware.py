import pytest
from django.test import override_settings


@pytest.mark.django_db
def test_no_index_header_added_outside_prod(client):
    """
    Test that responses tell crawlers not to index non-prod environments.
    """
    response = client.get("/robots.txt")
    assert response.status_code == 200
    assert response["X-Robots-Tag"] == "noindex, nofollow"


@pytest.mark.django_db
@override_settings(IS_PROD=True)
def test_no_index_header_omitted_in_prod(client):
    """
    Test that responses say nothing about indexing in prod.
    """
    response = client.get("/robots.txt")
    assert response.status_code == 200
    assert "X-Robots-Tag" not in response
