"""
Check to ensure middleware is annotating user models with the correct
authorization booleans. Used downstream by view permission checks.
"""

import pytest
from django.contrib.auth.models import Group

from accounts.models import User
from case.middleware import annotate_group_access


@pytest.mark.django_db
def test_is_group_annotations(
    user: User,
    paralegal_group: Group,
    lawyer_group: Group,
    coordinator_group: Group,
    admin_group: Group,
):
    """
    Ensure is_paralegal, is_coordinator, is_admin
    are set correctly by group access annotator.
    """
    assert not getattr(user, "is_paralegal", None)
    assert not getattr(user, "is_lawyer", None)
    assert not getattr(user, "is_coordinator", None)
    assert not getattr(user, "is_admin", None)

    annotate_group_access(user)
    assert not user.is_paralegal
    assert not user.is_lawyer
    assert not user.is_coordinator
    assert not user.is_admin

    # Set the user to only be in paralegal group.
    user.groups.set([paralegal_group])
    annotate_group_access(user)
    assert user.is_paralegal
    assert not user.is_lawyer
    assert not user.is_coordinator
    assert not user.is_admin

    # Set the user to only be in lawyer group.
    user.groups.set([lawyer_group])
    annotate_group_access(user)
    assert not user.is_paralegal
    assert user.is_lawyer
    assert not user.is_coordinator
    assert not user.is_admin

    # Set the user to only be in coordinator group.
    user.groups.set([coordinator_group])
    annotate_group_access(user)
    assert not user.is_paralegal
    assert not user.is_lawyer
    assert user.is_coordinator
    assert not user.is_admin

    # Set the user to only be in admin group.
    user.groups.set([admin_group])
    annotate_group_access(user)
    assert not user.is_paralegal
    assert not user.is_lawyer
    assert not user.is_coordinator
    assert user.is_admin

    # Set the user to be in all three groups.
    # Expect only highest permission to apply.
    user.groups.set([lawyer_group, coordinator_group, admin_group])
    annotate_group_access(user)
    assert not user.is_paralegal
    assert not user.is_lawyer
    assert not user.is_coordinator
    assert user.is_admin

    # Set the user to be a superuser in no groups.
    # Expect only highest permission to apply.
    user.groups.set([])
    user.is_superuser = True
    user.save()
    annotate_group_access(user)
    assert not user.is_paralegal
    assert not user.is_lawyer
    assert not user.is_coordinator
    assert not user.is_admin


@pytest.mark.django_db
def test_is_group_or_better_annotations(
    user: User,
    paralegal_group: Group,
    lawyer_group: Group,
    coordinator_group: Group,
    admin_group: Group,
):
    """
    Ensure is_paralegal_or_better, is_coordinator_or_better, is_admin_or_better
    are set correctly by group access annotator.
    """
    assert not getattr(user, "is_paralegal_or_better", None)
    assert not getattr(user, "is_lawyer_or_better", None)
    assert not getattr(user, "is_coordinator_or_better", None)
    assert not getattr(user, "is_admin_or_better", None)

    annotate_group_access(user)
    assert not user.is_paralegal_or_better
    assert not user.is_lawyer_or_better
    assert not user.is_coordinator_or_better
    assert not user.is_admin_or_better

    # Set the user to only be in paralegal group.
    user.groups.set([paralegal_group])
    annotate_group_access(user)
    assert user.is_paralegal_or_better
    assert not user.is_lawyer_or_better
    assert not user.is_coordinator_or_better
    assert not user.is_admin_or_better

    # Set the user to only be in lawyer group.
    user.groups.set([lawyer_group])
    annotate_group_access(user)
    assert user.is_paralegal_or_better
    assert user.is_lawyer_or_better
    assert not user.is_coordinator_or_better
    assert not user.is_admin_or_better

    # Set the user to only be in coordinator group.
    user.groups.set([coordinator_group])
    annotate_group_access(user)
    assert user.is_paralegal_or_better
    assert user.is_lawyer_or_better
    assert user.is_coordinator_or_better
    assert not user.is_admin_or_better

    # Set the user to only be in admin group.
    # Expect all permissions to apply.
    user.groups.set([admin_group])
    annotate_group_access(user)
    assert user.is_paralegal_or_better
    assert user.is_lawyer_or_better
    assert user.is_coordinator_or_better
    assert user.is_admin_or_better

    # Set the user to be in all three groups.
    # Expect all permissions to apply.
    user.groups.set([lawyer_group, lawyer_group, coordinator_group, admin_group])
    annotate_group_access(user)
    assert user.is_paralegal_or_better
    assert user.is_lawyer_or_better
    assert user.is_coordinator_or_better
    assert user.is_admin_or_better

    # Set the user to be a superuser in no groups.
    # Expect all permissions to apply.
    user.groups.set([])
    user.is_superuser = True
    user.save()
    annotate_group_access(user)
    assert user.is_paralegal_or_better
    assert user.is_lawyer_or_better
    assert user.is_coordinator_or_better
    assert user.is_admin_or_better
