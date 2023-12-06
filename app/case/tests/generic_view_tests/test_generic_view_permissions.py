"""
Tests to check authorization for generic view test cases.
"""
import pytest

from rest_framework.test import APIClient
from django.contrib.auth.models import Group
from rest_framework.reverse import reverse

from accounts.models import CaseGroups, User
from case.middleware import annotate_group_access
from case.tests.generic_view_tests.generic_view_test_cases import (
    APIViewTestCase,
    GENERIC_API_TEST_CASES,
)


TEST_GROUPS = [
    CaseGroups.ADMIN,
    CaseGroups.COORDINATOR,
    CaseGroups.PARALEGAL,
    CaseGroups.LAWYER,
]


@pytest.mark.django_db
@pytest.mark.parametrize("test_case", GENERIC_API_TEST_CASES)
@pytest.mark.parametrize("group_name", TEST_GROUPS)
def test_generic_list_view_requires_permissions(
    user_client: APIClient, user: User, test_case: APIViewTestCase, group_name: str
) -> None:
    """
    Ensure that a given view's API list view enforced the correct user permissions.
    """
    # Setup the user with a given group
    group, _ = Group.objects.get_or_create(name=group_name)
    user.groups.set([group])

    # Apply group annotations (usually done in middleware)
    annotate_group_access(user)
    is_authorized = test_case.test_read_permission(user)

    # Try view a list of items as the user (client logged in as user)
    list_view_name = f"{test_case.base_view_name}-list"
    url = reverse(list_view_name)
    response = user_client.get(url)

    if is_authorized:
        # Not forbidden
        assert response.status_code != 403
    else:
        # Is forbidden
        assert response.status_code == 403


@pytest.mark.django_db
@pytest.mark.parametrize("test_case", GENERIC_API_TEST_CASES)
@pytest.mark.parametrize("group_name", TEST_GROUPS)
def test_generic_create_view_requires_permissions(
    user_client: APIClient, user: User, test_case: APIViewTestCase, group_name: str
) -> None:
    """
    Ensure that a given view's API create view enforced the correct user permissions.
    """
    # Setup the user with a given group
    group, _ = Group.objects.get_or_create(name=group_name)
    user.groups.set([group])

    # Apply group annotations (usually done in middleware)
    annotate_group_access(user)
    is_authorized = test_case.test_write_permissions(user)

    # Try create a new item as the user (client logged in as user)
    list_view_name = f"{test_case.base_view_name}-list"
    url = reverse(list_view_name)
    response = user_client.post(url)

    if is_authorized:
        # Not forbidden
        assert response.status_code != 403
    else:
        # Is forbidden
        assert response.status_code == 403


@pytest.mark.django_db
@pytest.mark.parametrize("test_case", GENERIC_API_TEST_CASES)
@pytest.mark.parametrize("group_name", TEST_GROUPS)
def test_generic_detail_view_requires_permissions(
    user_client: APIClient, user: User, test_case: APIViewTestCase, group_name: str
) -> None:
    """
    Ensure that a given view's API detail view enforced the correct user permissions.
    """
    instance = test_case.factory()

    # Setup the user with a given group
    group, _ = Group.objects.get_or_create(name=group_name)
    user.groups.set([group])

    # Apply group annotations (usually done in middleware)
    annotate_group_access(user)
    is_authorized = test_case.test_read_permission(user)

    # Try view an item as the user (client logged in as user)
    detail_view_name = f"{test_case.base_view_name}-detail"
    url = reverse(detail_view_name, kwargs=dict(pk=instance.pk))
    response = user_client.get(url)

    if is_authorized:
        # Not forbidden
        assert response.status_code != 403
    else:
        # Is forbidden
        assert response.status_code == 403


@pytest.mark.django_db
@pytest.mark.parametrize("test_case", GENERIC_API_TEST_CASES)
@pytest.mark.parametrize("group_name", TEST_GROUPS)
def test_generic_update_view_requires_permissions(
    user_client: APIClient, user: User, test_case: APIViewTestCase, group_name: str
) -> None:
    """
    Ensure that a given view's API update view enforced the correct user permissions.
    """
    instance = test_case.factory()

    # Setup the user with a given group
    group, _ = Group.objects.get_or_create(name=group_name)
    user.groups.set([group])

    # Apply group annotations (usually done in middleware)
    annotate_group_access(user)
    is_authorized = test_case.test_write_permissions(user)

    # Try update an item as the user (client logged in as user)
    detail_view_name = f"{test_case.base_view_name}-detail"
    url = reverse(detail_view_name, kwargs=dict(pk=instance.pk))
    response = user_client.put(url)

    if is_authorized:
        # Not forbidden
        assert response.status_code != 403
    else:
        # Is forbidden
        assert response.status_code == 403


@pytest.mark.django_db
@pytest.mark.parametrize("test_case", GENERIC_API_TEST_CASES)
@pytest.mark.parametrize("group_name", TEST_GROUPS)
def test_generic_delete_view_requires_permissions(
    user_client: APIClient, user: User, test_case: APIViewTestCase, group_name: str
) -> None:
    """
    Ensure that a given view's API delete view enforced the correct user permissions.
    """
    instance = test_case.factory()

    # Setup the user with a given group
    group, _ = Group.objects.get_or_create(name=group_name)
    user.groups.set([group])

    # Apply group annotations (usually done in middleware)
    annotate_group_access(user)
    is_authorized = test_case.test_write_permissions(user)

    # Try delete an item as the user (client logged in as user)
    detail_view_name = f"{test_case.base_view_name}-detail"
    url = reverse(detail_view_name, kwargs=dict(pk=instance.pk))
    response = user_client.delete(url)

    if is_authorized:
        # Not forbidden
        assert response.status_code != 403
    else:
        # Is forbidden
        assert response.status_code == 403
