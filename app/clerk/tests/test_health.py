from unittest.mock import patch

import pytest
from django.db import DatabaseError
from django.urls import reverse


@pytest.mark.django_db
def test_health_ok(client):
    response = client.get(reverse("health"))
    assert response.status_code == 200
    assert response.content == b"ok"


@pytest.mark.django_db
def test_health_database_unavailable(client):
    with patch(
        "clerk.views.connection.ensure_connection", side_effect=DatabaseError("down")
    ):
        response = client.get(reverse("health"))
    assert response.status_code == 503
