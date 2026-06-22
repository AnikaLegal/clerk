import pytest
from accounts.models import User
from case.middleware import annotate_group_access
from case.serializers import ServiceSerializer
from core.factories import IssueFactory, ServiceFactory
from core.models.service import (
    DiscreteServiceType,
    OngoingServiceType,
    Service,
    ServiceCategory,
)
from rest_framework.reverse import reverse


@pytest.mark.django_db
def test_case_service_list_api(superuser_client):
    service = ServiceFactory()
    ServiceFactory(issue=service.issue)

    url = reverse("case-api-service-list", args=(service.issue.pk,))
    response = superuser_client.get(url)

    assert response.status_code == 200, response.json()
    data = response.json()
    assert len(data) == 2


@pytest.mark.django_db
def test_case_service_create_api(superuser_client, superuser: User):
    # Instantiate with build so that it returns an unsaved instance. We just
    # want the data so we can test creating it ourselves.
    service = ServiceFactory.build(issue=IssueFactory())
    assert service.id is None
    assert Service.objects.count() == 0

    url = reverse("case-api-service-list", args=(service.issue.pk,))
    request_data = ServiceSerializer(service).data
    request_data.pop("id", None)
    request_data.pop("issue_id", None)

    response = superuser_client.post(url, data=request_data)
    assert response.status_code == 201, response.json()
    response_data = ServiceSerializer(response.json()).data

    # Compare response and request data.
    assert response_data["id"] is not None
    for field_name in request_data.keys():
        assert request_data[field_name] == response_data[field_name]
    assert response_data["issue_id"] == str(service.issue.pk)
    assert Service.objects.count() == 1


@pytest.mark.django_db
def test_case_service_get_api(superuser_client):
    service = ServiceFactory()

    url = reverse("case-api-service-detail", args=(service.issue.pk, service.pk))
    response = superuser_client.get(url)

    assert response.status_code == 200, response.json()
    data = response.json()
    assert data["id"] == service.pk


@pytest.mark.django_db
def test_case_service_update_api(superuser_client):
    service = ServiceFactory(
        category=ServiceCategory.DISCRETE,
        type=DiscreteServiceType.LEGAL_TASK,
        notes="discrete legal task service",
    )

    url = reverse("case-api-service-detail", args=(service.issue.pk, service.pk))
    response = superuser_client.patch(
        url,
        data={
            "category": ServiceCategory.ONGOING,
            "type": OngoingServiceType.LEGAL_SUPPORT,
            "notes": "ongoing legal support service",
        },
    )

    assert response.status_code == 200, response.json()
    data = response.json()
    assert data["category"] == ServiceCategory.ONGOING
    assert data["type"] == OngoingServiceType.LEGAL_SUPPORT
    assert data["notes"] == "ongoing legal support service"


@pytest.mark.django_db
def test_case_service_delete_api(superuser_client):
    service = ServiceFactory()
    assert Service.objects.count() == 1

    url = reverse("case-api-service-detail", args=(service.issue.pk, service.pk))
    response = superuser_client.delete(url)

    assert response.status_code == 204
    # Services use soft deletes so we have to exclude deleted services below to
    # get the correct count.
    assert Service.objects.exclude(is_deleted=True).count() == 0


@pytest.mark.django_db
def test_case_list_api__filter(superuser_client):
    issue = IssueFactory()
    service_a = ServiceFactory(issue=issue, category=ServiceCategory.DISCRETE)

    url = reverse("case-api-service-list", args=(issue.pk,))

    # No search results
    response = superuser_client.get(url, {"category": ServiceCategory.ONGOING})
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 0

    service_b = ServiceFactory(issue=issue, category=ServiceCategory.ONGOING)

    # One search result
    response = superuser_client.get(url, {"category": ServiceCategory.ONGOING})
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["id"] == service_b.pk

    response = superuser_client.get(url, {"type": service_a.type})
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["id"] == service_a.pk


@pytest.mark.django_db
@pytest.mark.parametrize(
    "test_user, group_name, expected_status",
    [
        ("unassigned_user", None, 403),
        ("unassigned_paralegal", "paralegal_group", 403),
    ],
)
def test_case_service_api_perms__as_user_without_access(
    test_user: str,
    group_name: str | None,
    expected_status: int,
    user_client,
    user: User,
    request,
):
    """
    Test create, list, display, update & delete of a service as a paralegal
    not assigned to the case to which the service belongs.
    """
    if group_name is not None:
        group = request.getfixturevalue(group_name)
        user.groups.set([group])

    annotate_group_access(user)

    # 1. Create.
    service = ServiceFactory.build(issue=IssueFactory())
    assert service.id is None
    assert Service.objects.count() == 0

    url = reverse("case-api-service-list", args=(service.issue.pk,))
    request_data = ServiceSerializer(service).data
    request_data.pop("id", None)
    request_data.pop("issue_id", None)

    response = user_client.post(url, data=request_data)
    assert response.status_code == expected_status

    # Need to create a service to use in the following tests.
    service = ServiceFactory()

    # 2. List.
    url = reverse("case-api-service-list", args=(service.issue.pk,))
    response = user_client.get(url)
    assert response.status_code == expected_status

    # 3. Display.
    url = reverse("case-api-service-detail", args=(service.issue.pk, service.pk))
    response = user_client.get(url)
    assert response.status_code == expected_status

    # 4. Update.
    url = reverse("case-api-service-detail", args=(service.issue.pk, service.pk))
    response = user_client.patch(url, data={"notes": "UPDATE TEST"})
    assert response.status_code == expected_status

    # 3. Delete.
    url = reverse("case-api-service-detail", args=(service.issue.pk, service.pk))
    response = user_client.delete(url)
    assert response.status_code == expected_status


@pytest.mark.django_db
@pytest.mark.parametrize(
    "test_user, group_name, is_assigned",
    [
        ("assigned_paralegal", "paralegal_group", True),
        ("assigned_coordinator", "coordinator_group", True),
        ("unassigned_coordinator", "coordinator_group", False),
    ],
)
def test_case_service_api_perms__as_user_with_access(
    test_user: str,
    group_name: str,
    is_assigned: bool,
    user_client,
    user: User,
    request,
):
    """
    Test create, list, display, update & delete of a service as a paralegal
    assigned to the case to which the service belongs.
    """
    group = request.getfixturevalue(group_name)
    user.groups.set([group])
    annotate_group_access(user)

    issue = IssueFactory()
    if is_assigned:
        issue.paralegal = user
        issue.save()

    # 1. Create.
    service = ServiceFactory.build(issue=issue)
    assert service.id is None
    assert Service.objects.count() == 0

    url = reverse("case-api-service-list", args=(service.issue.pk,))
    request_data = ServiceSerializer(service).data
    request_data.pop("id", None)
    request_data.pop("issue_id", None)

    response = user_client.post(url, data=request_data)
    assert response.status_code == 201
    data = response.json()
    service_id = data["id"]

    # 2. List.
    url = reverse("case-api-service-list", args=(service.issue.pk,))
    response = user_client.get(url)
    assert response.status_code == 200

    # 3. Display.
    url = reverse("case-api-service-detail", args=(service.issue.pk, service_id))
    response = user_client.get(url)
    assert response.status_code == 200

    # 4. Update.
    url = reverse("case-api-service-detail", args=(service.issue.pk, service_id))
    response = user_client.patch(url, data={"notes": "UPDATE TEST"})
    assert response.status_code == 200

    # 3. Delete.
    url = reverse("case-api-service-detail", args=(service.issue.pk, service_id))
    response = user_client.delete(url)
    assert response.status_code == 204
