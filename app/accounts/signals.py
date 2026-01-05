from auditlog.models import LogEntry
from auditlog.receivers import post_log
from django.contrib.auth.models import Group
from django.db.models.signals import m2m_changed
from django.dispatch import receiver

from accounts import events
from accounts.models import User


@receiver(post_log, sender=User)
def post_log_user(sender, instance, action, changes, **kwargs):
    user: User = instance
    if action == LogEntry.Action.CREATE:
        if user.is_active:
            events.user_activated.send(sender=User, user=user)
    elif action == LogEntry.Action.UPDATE:
        if "is_active" in changes:
            old_value, new_value = changes["is_active"]
            if not old_value and new_value:
                events.user_activated.send(sender=User, user=user)
            elif old_value and not new_value:
                events.user_deactivated.send(sender=User, user=user)
    elif action == LogEntry.Action.DELETE:
        if user.is_active:
            events.user_deactivated.send(sender=User, user=user)


@receiver(m2m_changed, sender=User.groups.through)
def m2m_changed_user_groups(sender, instance, action, **kwargs):
    if kwargs.get("reverse"):
        # Do nothing if it's a Group instance rather than a User.
        return

    user: User = instance
    if not user.is_active:
        return

    pk_set = kwargs.get("pk_set")
    if pk_set is None:
        return

    # Clear cached role to ensure it is recalculated based on current groups.
    user.clear_role()

    # Emit appropriate events based on the action.
    queryset = Group.objects.filter(pk__in=pk_set)
    if action == "post_add":
        for group in queryset:
            events.user_added_to_group.send(
                sender=User,
                user=user,
                group=group,
            )
    elif action == "post_remove":
        for group in queryset:
            events.user_removed_from_group.send(
                sender=User,
                user=user,
                group=group,
            )
