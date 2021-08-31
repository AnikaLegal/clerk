import logging
from typing import Tuple
from django.conf import settings

from core.models import Issue
from emails.models import Email

logger = logging.getLogger(__name__)


def build_clerk_address(email: Email):
    """
    FIXME: TEST ME.
    """
    assert email.issue
    issue_prefix = str(email.issue.id).split("-")[0]
    email = f"case.{issue_prefix}@{settings.EMAIL_DOMAIN}"
    return f"Anika Legal <{email}>"


def parse_clerk_address(email: Email) -> Tuple[str, Issue]:
    """
    Returns to address and issue or None, None
    FIXME: TEST ME.
    """
    assert False, "TODO"
    # FIXME: BROKEN

    user, domain = email_addr.split("@")
    assert domain == settings.EMAIL_DOMAIN, f"Incorrect domain {domain}"

    try:
        user_parts = user.split(".")
        issue_prefix = user_parts[-1]
        return Issue.objects.get(id__startswith=issue_prefix)
    except:
        logger.exception(f"Could not parse email address {email_addr}")
