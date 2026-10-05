import pytest
from django.test import Client


@pytest.mark.django_db
def test_unknown_clerk_path_renders_404_page_for_anonymous_user(client: Client):
    response = client.get("/clerk/this/path/does/not/exist/")

    assert response.status_code == 404
    assert b"REACT_CONTEXT" in response.content
