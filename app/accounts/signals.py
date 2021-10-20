# User / Group / Permission signals go here
# set_up_coordinator / tear_down_coordinator
from django.contrib.auth.models import Group
from django.db.models.signals import m2m_changed
from django.dispatch import receiver

from core.models import Issue
from accounts.models import User, CaseGroups
from microsoft.service import (
    remove_user_from_case,
    set_up_coordinator,
    tear_down_coordinator,
)


POST_ADD = "post_add"
POST_REMOVE = "post_remove"
COORDINATOR_GROUPS = [CaseGroups.COORDINATOR, CaseGroups.ADMIN]

# https://docs.djangoproject.com/en/3.2/ref/signals/#m2m-changed
@receiver(m2m_changed, sender=User.groups.through)
def post_save_group(sender, instance, action, **kwargs):
    if kwargs.get("reverse"):
        # Do nothing if it's a Group instance rather than a User.
        return

    user = instance
    if action == POST_ADD:
        if not user.is_active:
            return

        # We've added these groups to the user.
        is_now_coordinator_or_better = Group.objects.filter(
            pk__in=kwargs["pk_set"], name__in=COORDINATOR_GROUPS
        ).exists()
        if is_now_coordinator_or_better:
            # If the user becomes a coordinator or is a super user,
            # then try set up their Microsoft account permissions.
            set_up_coordinator(user)

    elif action == POST_REMOVE:
        # We've removed these groups from the user.
        is_still_coordinator_or_better = user.groups.filter(
            name__in=COORDINATOR_GROUPS
        ).exists()
        if (not user.is_active) or (not is_still_coordinator_or_better):
            # If the user is not coordinator and is not a super user,
            # then try tear down their Microsoft account permissions.
            tear_down_coordinator(user)

        is_paralegal_or_better = user.groups.filter(name__in=CaseGroups.GROUPS).exists()
        if (not user.is_active) or (not is_paralegal_or_better):
            # If the user is not a paralegal or better then tear down
            # their Microsoft account permissions for every case they are assigned to.
            issues = Issue.objects.filter(paralegal=user)
            for issue in issues:
                remove_user_from_case(user, issue)
