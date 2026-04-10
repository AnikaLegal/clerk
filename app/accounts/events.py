"""Domain signals for user access and permissions.

Define signal objects that describe intent (user added/removed from case,
groups changed, activation toggles). Handlers subscribe to these signals and
delegate to a `UserAccessManager` obtained from the registry.
"""

from django.dispatch import Signal

# Sent when a user is given access to a case (issue). kwargs: user, issue
user_added_to_case = Signal()

# Sent when a user's access to a case should be removed. kwargs: user, issue
user_removed_from_case = Signal()

# Sent when the user's groups change. kwargs: user, group
user_added_to_group = Signal()
user_removed_from_group = Signal()

# Sent when a user's account has been activated or deactivated. kwargs: user
user_activated = Signal()
user_deactivated = Signal()
