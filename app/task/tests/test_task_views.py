import pytest
from accounts.models import User
from case.middleware import annotate_group_access
from conftest import schema_tester
from core.factories import UserFactory
from rest_framework.reverse import reverse
from rest_framework.test import APIClient
from task.factories import TaskFactory


@pytest.mark.django_db
def test_task_list_view__with_no_access(user_client: APIClient, user: User):
    """
    Logged in, but otherwise unauthorized, users can fetch tasks but no results
    """
    annotate_group_access(user)
    url = reverse("task-api-list")

    TaskFactory()  # There's a task but the user can't see it

    response = user_client.get(url)
    assert response.status_code == 200
    assert response.json() == []
    schema_tester.validate_response(response=response)


@pytest.mark.django_db
def test_task_list_view__as_paralegal_with_no_access_to_task(
    user_client: APIClient,
    user: User,
    paralegal_group,
):
    """
    Paralegal users can fetch tasks but no results because they're not assigned.
    """
    user.groups.set([paralegal_group])
    annotate_group_access(user)
    url = reverse("task-api-list")

    TaskFactory()

    response = user_client.get(url)
    assert response.status_code == 200
    assert response.json() == []
    schema_tester.validate_response(response=response)


@pytest.mark.django_db
def test_task_list_view__as_paralegal_with_no_access_to_issue(
    user_client: APIClient,
    user: User,
    paralegal_group,
):
    """
    Paralegal users can fetch tasks but no results because they're not assigned
    to the issue to which the task is related.
    """
    user.groups.set([paralegal_group])
    annotate_group_access(user)
    url = reverse("task-api-list")

    TaskFactory(assigned_to=user, issue__paralegal=UserFactory())

    response = user_client.get(url)
    assert response.status_code == 200
    assert response.json() == []
    schema_tester.validate_response(response=response)


@pytest.mark.django_db
def test_task_list_view__as_paralegal_with_access_to_issue_but_no_access_to_task(
    user_client: APIClient,
    user: User,
    paralegal_group,
):
    """
    Paralegal users can fetch tasks but no results because even though they are
    assigned to the issue they're not assigned to the task.
    """
    user.groups.set([paralegal_group])
    annotate_group_access(user)
    url = reverse("task-api-list")

    TaskFactory(issue__paralegal=user)

    response = user_client.get(url)
    assert response.status_code == 200
    assert response.json() == []
    schema_tester.validate_response(response=response)


@pytest.mark.django_db
def test_task_list_view__as_paralegal_with_access(
    user_client: APIClient,
    user: User,
    paralegal_group,
):
    """
    Paralegal users can fetch tasks and see results when they're the assigned to
    the task and assigned to the issue.
    """
    user.groups.set([paralegal_group])
    annotate_group_access(user)
    url = reverse("task-api-list")

    task = TaskFactory(assigned_to=user, issue__paralegal=user)

    # Other tasks but no access.
    TaskFactory(assigned_to=user, issue__paralegal=UserFactory())
    TaskFactory(issue__paralegal=user)
    TaskFactory()

    response = user_client.get(url)
    assert response.status_code == 200
    results = response.json()
    assert len(results) == 1
    assert results[0]["id"] == task.pk
    schema_tester.validate_response(response=response)


@pytest.mark.django_db
def test_task_list_view__as_coordinator(
    user_client: APIClient,
    user: User,
    coordinator_group,
):
    """
    Coordinator users can see all tasks.
    """
    user.groups.set([coordinator_group])
    annotate_group_access(user)
    url = reverse("task-api-list")

    TaskFactory(assigned_to=user, issue__paralegal=user)
    TaskFactory(assigned_to=user, issue__paralegal=UserFactory())
    TaskFactory(issue__paralegal=user)
    TaskFactory()

    response = user_client.get(url)
    assert response.status_code == 200
    results = response.json()
    assert len(results) == 4
    schema_tester.validate_response(response=response)


@pytest.mark.django_db
def test_task_list_view__search(superuser_client: APIClient):
    task_1 = TaskFactory(name="task_1")
    task_2 = TaskFactory(name="task_2")
    task_3 = TaskFactory(name="task_3")
    url = reverse("task-api-list")

    # No search results
    response = superuser_client.get(url, {"q": "xxxxxxxxxxxx"})
    assert response.status_code == 200
    results = response.json()
    assert len(results) == 0

    # One search result
    response = superuser_client.get(url, {"q": "task_1"})
    assert response.status_code == 200
    results = response.json()
    assert len(results) == 1
    assert results[0]["id"] == task_1.pk
    schema_tester.validate_response(response=response)
