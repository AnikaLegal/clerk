"""
Microsoft-related events.
"""

from django.dispatch import Signal

# Sent when a user's account has been created or deleted. kwargs: user, ms password
ms_account_created = Signal()
