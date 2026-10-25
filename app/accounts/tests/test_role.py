import pytest
from django.contrib.auth.models import AnonymousUser

from accounts.role import UserRole


def _assert_all_false(role: UserRole):
    assert role.is_admin is False
    assert role.is_coordinator is False
    assert role.is_lawyer is False
    assert role.is_paralegal is False

    assert role.is_admin_or_better is False
    assert role.is_coordinator_or_better is False
    assert role.is_lawyer_or_better is False
    assert role.is_paralegal_or_better is False


@pytest.mark.django_db
def test_no_groups_defaults_false(user):
    role = UserRole(user)
    _assert_all_false(role)


@pytest.mark.django_db
def test_superuser_role(superuser):
    role = UserRole(superuser)
    assert role.is_admin is False
    assert role.is_coordinator is False
    assert role.is_lawyer is False
    assert role.is_paralegal is False

    assert role.is_admin_or_better is True
    assert role.is_coordinator_or_better is True
    assert role.is_lawyer_or_better is True
    assert role.is_paralegal_or_better is True


@pytest.mark.django_db
def test_admin_group_role(admin_user):
    role = UserRole(admin_user)
    assert role.is_admin is True
    assert role.is_coordinator is False
    assert role.is_lawyer is False
    assert role.is_paralegal is False

    assert role.is_admin_or_better is True
    assert role.is_coordinator_or_better is True
    assert role.is_lawyer_or_better is True
    assert role.is_paralegal_or_better is True


@pytest.mark.django_db
def test_coordinator_group_role(coordinator_user):
    role = UserRole(coordinator_user)
    assert role.is_admin is False
    assert role.is_coordinator is True
    assert role.is_lawyer is False
    assert role.is_paralegal is False

    assert role.is_admin_or_better is False
    assert role.is_coordinator_or_better is True
    assert role.is_lawyer_or_better is True
    assert role.is_paralegal_or_better is True


@pytest.mark.django_db
def test_lawyer_group_role(lawyer_user):
    role = UserRole(lawyer_user)
    assert role.is_admin is False
    assert role.is_coordinator is False
    assert role.is_lawyer is True
    assert role.is_paralegal is False

    assert role.is_admin_or_better is False
    assert role.is_coordinator_or_better is False
    assert role.is_lawyer_or_better is True
    assert role.is_paralegal_or_better is True


@pytest.mark.django_db
def test_paralegal_group_role(paralegal_user):
    role = UserRole(paralegal_user)
    assert role.is_admin is False
    assert role.is_coordinator is False
    assert role.is_lawyer is False
    assert role.is_paralegal is True

    assert role.is_admin_or_better is False
    assert role.is_coordinator_or_better is False
    assert role.is_lawyer_or_better is False
    assert role.is_paralegal_or_better is True


@pytest.mark.django_db
def test_group_precedence_with_admin_present(
    user, admin_group, lawyer_group, coordinator_group, paralegal_group
):
    # Any membership including ADMIN should result in admin role, regardless of order.
    user.groups.set([admin_group, lawyer_group, coordinator_group, paralegal_group])

    role = UserRole(user)
    assert role.is_admin is True
    assert role.is_coordinator is False
    assert role.is_lawyer is False
    assert role.is_paralegal is False

    user.groups.set([paralegal_group, coordinator_group, lawyer_group, admin_group])

    role = UserRole(user)
    assert role.is_admin is True
    assert role.is_coordinator is False
    assert role.is_lawyer is False
    assert role.is_paralegal is False


@pytest.mark.django_db
def test_group_precedence_without_admin(
    user, lawyer_group, coordinator_group, paralegal_group
):
    # With COORDINATOR and LAWYER present, coordinator wins.
    user.groups.set([lawyer_group, coordinator_group])

    role = UserRole(user)
    assert role.is_coordinator is True
    assert role.is_admin is False
    assert role.is_lawyer is False
    assert role.is_paralegal is False

    # With LAWYER and PARALEGAL present, lawyer wins.
    user.groups.set([paralegal_group, lawyer_group])
    role = UserRole(user)
    assert role.is_lawyer is True
    assert role.is_admin is False
    assert role.is_coordinator is False
    assert role.is_paralegal is False


@pytest.mark.django_db
def test_is_in_group_properties_reflect_membership(user, admin_group, lawyer_group):
    user.groups.set([admin_group, lawyer_group])
    role = UserRole(user)
    assert role.is_in_admin_group is True
    assert role.is_in_lawyer_group is True
    assert role.is_in_coordinator_group is False
    assert role.is_in_paralegal_group is False


@pytest.mark.django_db
def test_superuser_with_group_memberships_still_no_base_role(
    user, admin_group, lawyer_group
):
    user.groups.set([admin_group, lawyer_group])
    user.is_superuser = True
    user.save()

    role = UserRole(user)
    # base roles False
    assert role.is_admin is False
    assert role.is_coordinator is False
    assert role.is_lawyer is False
    assert role.is_paralegal is False
    # all ..._or_better True
    assert role.is_admin_or_better is True
    assert role.is_coordinator_or_better is True
    assert role.is_lawyer_or_better is True
    assert role.is_paralegal_or_better is True
    # membership properties still reflect group set
    assert role.is_in_admin_group is True
    assert role.is_in_lawyer_group is True


@pytest.mark.django_db
def test_annotate_user_attaches_attrs(user, lawyer_group):
    user.groups.set([lawyer_group])
    # ensure attributes are not present beforehand
    for attr in (
        "is_admin",
        "is_coordinator",
        "is_lawyer",
        "is_paralegal",
        "is_admin_or_better",
        "is_coordinator_or_better",
        "is_lawyer_or_better",
        "is_paralegal_or_better",
    ):
        assert not hasattr(user, attr)
    # annotate and assert attributes added with correct values
    UserRole.annotate_user(user)
    assert user.is_lawyer is True
    assert user.is_lawyer_or_better is True
    assert user.is_admin is False
    assert user.is_admin_or_better is False
    assert user.is_coordinator is False
    assert user.is_coordinator_or_better is False
    assert user.is_paralegal is False
    assert user.is_paralegal_or_better is True


@pytest.mark.django_db
def test_reset_recomputes_on_group_change(user, paralegal_group, coordinator_group):
    user.groups.set([paralegal_group])
    role = UserRole(user)
    assert role.is_paralegal is True

    # Change groups to coordinator
    user.groups.set([coordinator_group])
    role.reset()
    assert role.is_coordinator is True
    assert role.is_paralegal is False

    # Change groups to none
    user.groups.set([])
    role.reset()
    _assert_all_false(role)


def test_flags_for_anonymous_user_is_all_false():
    flags = UserRole.flags_for(AnonymousUser())

    assert set(flags.values()) == {False}
    assert "is_admin" in flags
    assert "is_paralegal_or_better" in flags


@pytest.mark.django_db
def test_flags_for_annotated_user(user, admin_group):
    user.groups.set([admin_group])
    UserRole.annotate_user(user)

    flags = UserRole.flags_for(user)

    assert flags["is_admin"] is True
    assert flags["is_admin_or_better"] is True
    assert flags["is_paralegal"] is False
