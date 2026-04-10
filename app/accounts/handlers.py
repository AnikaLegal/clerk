"""
Handlers for domain signals that delegate to the UserAccessManager.

This module contains the centralised logic that responds to domain-level
signals and performs the necessary side effects via a pluggable manager.
"""

import logging

from django.dispatch import receiver

from accounts import events
from accounts.registry import get_user_event_manager

logger = logging.getLogger(__name__)


@receiver(events.user_added_to_case)
def handle_user_added_to_case(sender, user, issue, **kwargs):
    mgr = get_user_event_manager()
    try:
        mgr.user_added_to_case(user, issue)
    except Exception:
        logger.exception(
            "Failure handling user event: user %s added to case %s", user, issue
        )


@receiver(events.user_removed_from_case)
def handle_user_removed_from_case(sender, user, issue, **kwargs):
    mgr = get_user_event_manager()
    try:
        mgr.user_removed_from_case(user, issue)
    except Exception:
        logger.exception(
            "Failure handling user event: user %s removed from case %s", user, issue
        )


@receiver(events.user_activated)
def handle_user_activated(sender, user, **kwargs):
    mgr = get_user_event_manager()
    try:
        mgr.user_activated(user)
    except Exception:
        logger.exception("Failure handling user event: user %s activated", user)


@receiver(events.user_deactivated)
def handle_user_deactivated(sender, user, **kwargs):
    mgr = get_user_event_manager()
    try:
        mgr.user_deactivated(user)
    except Exception:
        logger.exception("Failure handling user event: user %s deactivated", user)


@receiver(events.user_added_to_group)
def handle_user_added_to_group(sender, user, group, **kwargs):
    mgr = get_user_event_manager()
    try:
        mgr.user_added_to_group(user, group)
    except Exception:
        logger.exception(
            "Failure handling user event: user %s added to group %s", user, group
        )


@receiver(events.user_removed_from_group)
def handle_user_removed_from_group(sender, user, group, **kwargs):
    mgr = get_user_event_manager()
    try:
        mgr.user_removed_from_group(user, group)
    except Exception:
        logger.exception(
            "Failure handling user event: user %s removed from group %s", user, group
        )
