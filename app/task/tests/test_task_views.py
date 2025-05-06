import uuid

import pytest
from conftest import schema_tester
from core.factories import UserFactory
from rest_framework.reverse import reverse
from rest_framework.test import APIClient
from task.factories import TaskFactory
from task.helpers import get_coordinators_user
from task.models import Task


@pytest.mark.django_db
@pytest.mark.parametrize(
    "user_fixture", ["unprivileged_user", "paralegal_user", "lawyer_user"]
)
def test_task_list_view__unassigned_user(user_fixture, user_client: APIClient, request):
    """
    Users can fetch tasks but no results because they're not assigned.
    """
    user = request.getfixturevalue(user_fixture)
    TaskFactory()  # There's a task but the user can't see it
    assert Task.objects.count() == 1

    response = user_client.get(reverse("task-api-list"))
    assert response.status_code == 200
    data = response.json()
    assert data["results"] == []
    schema_tester.validate_response(response=response)


@pytest.mark.django_db
@pytest.mark.parametrize("user_fixture", ["paralegal_user", "lawyer_user"])
def test_task_list_view__user_assigned_to_task_but_not_issue(
    user_fixture,
    user_client: APIClient,
    request,
):
    """
    Users can fetch tasks but no results because they're not assigned to the
    issue to which the task is related.
    """
    user = request.getfixturevalue(user_fixture)
    TaskFactory(assigned_to=user, issue__paralegal=UserFactory())
    assert Task.objects.count() == 1

    response = user_client.get(reverse("task-api-list"))
    assert response.status_code == 200
    data = response.json()
    assert data["results"] == []
    schema_tester.validate_response(response=response)


@pytest.mark.django_db
def test_task_list_view__as_paralegal_assigned_to_issue_but_not_task(
    paralegal_user,
    user_client: APIClient,
):
    """
    Paralegal users can fetch tasks but no results because even though they are
    assigned to the issue they're not assigned to the task.
    """
    TaskFactory(issue__paralegal=paralegal_user)
    assert Task.objects.count() == 1

    response = user_client.get(reverse("task-api-list"))
    assert response.status_code == 200
    data = response.json()
    assert data["results"] == []
    schema_tester.validate_response(response=response)


@pytest.mark.django_db
def test_task_list_view__as_assigned_paralegal(
    paralegal_user,
    user_client: APIClient,
):
    """
    Paralegal users can fetch tasks and see results when they're the assigned to
    the task and assigned to the issue.
    """
    task = TaskFactory(assigned_to=paralegal_user, issue__paralegal=paralegal_user)
    # Other tasks but no access.
    TaskFactory(assigned_to=paralegal_user, issue__paralegal=UserFactory())
    TaskFactory(issue__paralegal=paralegal_user)
    TaskFactory()
    assert Task.objects.count() == 4

    response = user_client.get(reverse("task-api-list"))
    assert response.status_code == 200
    data = response.json()
    results = data["results"]
    assert len(results) == 1
    assert results[0]["id"] == task.pk
    schema_tester.validate_response(response=response)


@pytest.mark.django_db
def test_task_list_view__as_assigned_lawyer(
    lawyer_user,
    user_client: APIClient,
):
    """
    Lawyer users can see all of the tasks related to their assigned issues.
    """
    task_1 = TaskFactory(
        assigned_to=lawyer_user,
        issue__lawyer=lawyer_user,
    )
    task_2 = TaskFactory(issue__lawyer=lawyer_user)
    # Other tasks but no access.
    TaskFactory(assigned_to=lawyer_user, issue__lawyer=UserFactory())
    TaskFactory(issue__paralegal=lawyer_user)
    TaskFactory()
    assert Task.objects.count() == 5

    response = user_client.get(reverse("task-api-list"))
    assert response.status_code == 200
    data = response.json()
    results = data["results"]
    assert len(results) == 2
    assert {results[0]["id"], results[1]["id"]} == {task_1.pk, task_2.pk}
    schema_tester.validate_response(response=response)


@pytest.mark.django_db
def test_task_list_view__as_coordinator(
    coordinator_user,
    user_client: APIClient,
):
    """
    Coordinator users can see all tasks.
    """
    TaskFactory(assigned_to=coordinator_user, issue__paralegal=coordinator_user)
    TaskFactory(assigned_to=coordinator_user, issue__paralegal=UserFactory())
    TaskFactory(issue__paralegal=coordinator_user)
    TaskFactory()
    assert Task.objects.count() == 4

    response = user_client.get(reverse("task-api-list"))
    assert response.status_code == 200
    data = response.json()
    assert len(data["results"]) == 4
    schema_tester.validate_response(response=response)


@pytest.mark.django_db
def test_task_list_view__search_by_q(superuser_client: APIClient):
    task_1 = TaskFactory(name="task_1")
    task_2 = TaskFactory(name="task_2")
    assert Task.objects.count() == 2

    url = reverse("task-api-list")

    # No search results
    response = superuser_client.get(url, {"q": "xxxxxxxxxxxx"})
    assert response.status_code == 200
    data = response.json()
    assert len(data["results"]) == 0

    # One search result
    response = superuser_client.get(url, {"q": "task_1"})
    assert response.status_code == 200
    data = response.json()
    results = data["results"]
    assert len(results) == 1
    assert results[0]["id"] == task_1.pk
    schema_tester.validate_response(response=response)


@pytest.mark.django_db
def test_task_list_view__filter_by_issue(superuser_client: APIClient):
    task_1 = TaskFactory()
    task_2 = TaskFactory()
    assert Task.objects.count() == 2

    url = reverse("task-api-list")

    # No search results
    response = superuser_client.get(url, {"issue": str(uuid.uuid4())})
    assert response.status_code == 200
    data = response.json()
    assert len(data["results"]) == 0

    # One search result
    response = superuser_client.get(url, {"issue": str(task_1.issue.pk)})
    assert response.status_code == 200
    data = response.json()
    results = data["results"]
    assert len(results) == 1
    assert results[0]["id"] == task_1.pk

    schema_tester.validate_response(response=response)


@pytest.mark.django_db
def test_task_list_view__filter_by_assigned_to(superuser_client: APIClient):
    task_1 = TaskFactory()
    task_2 = TaskFactory()
    assert Task.objects.count() == 2

    url = reverse("task-api-list")

    # No search results
    user = UserFactory()
    response = superuser_client.get(url, {"assigned_to": user.pk})
    assert response.status_code == 200
    data = response.json()
    assert len(data["results"]) == 0

    # One search result
    response = superuser_client.get(url, {"assigned_to": task_1.assigned_to.pk})
    assert response.status_code == 200
    data = response.json()
    results = data["results"]
    assert len(results) == 1
    assert results[0]["id"] == task_1.pk

    schema_tester.validate_response(response=response)


@pytest.mark.django_db
def test_task_list_view__filter_by_assigned_to_coordinator_user(
    user_client, coordinator_user
):
    """
    Tasks assigned to the special "coordinators@anikalegal.com" user are also
    listed when filtering tasks assigned to a specific coordinator user.
    """
    task_1 = TaskFactory(assigned_to=coordinator_user)
    task_2 = TaskFactory(assigned_to=get_coordinators_user())
    task_3 = TaskFactory()
    assert Task.objects.count() == 3

    # Two search result
    response = user_client.get(
        reverse("task-api-list"), {"assigned_to": coordinator_user.pk}
    )
    assert response.status_code == 200
    data = response.json()
    results = data["results"]
    assert len(results) == 2
    assert set(x["id"] for x in results) == {task_1.pk, task_2.pk}

    schema_tester.validate_response(response=response)
