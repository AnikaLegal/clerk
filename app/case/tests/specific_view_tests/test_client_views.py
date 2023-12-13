import pytest
from rest_framework.test import APIClient
from rest_framework.reverse import reverse

from core.factories import ClientFactory, IssueFactory
from case.middleware import annotate_group_access


@pytest.mark.django_db
def test_client_view_object_permissions(
    user, user_client: APIClient, paralegal_group, coordinator_group
):
    client = ClientFactory()
    issue = IssueFactory(client=client)
    url = reverse("client-api-detail", args=(client.pk,))

    # Coordinator can access
    user.groups.set([coordinator_group])
    annotate_group_access(user)
    response = user_client.patch(url, {"first_name": "A"}, format="json")
    assert response.status_code == 200, response.json()

    user.groups.set([paralegal_group])
    annotate_group_access(user)
    response = user_client.patch(url, {"first_name": "B"}, format="json")

    # Paralegal can't access, no object permissions
    assert response.status_code == 403, response.json()

    issue.paralegal = user
    issue.save()

    # Paralegal can access with object permissions
    response = user_client.patch(url, {"first_name": "C"}, format="json")
    assert response.status_code == 200, response.json()
