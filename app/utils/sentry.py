import os
from functools import wraps
import logging

from sentry_sdk import capture_exception

SENTRY_DSN = os.environ.get("RAVEN_DSN")

logger = logging.getLogger(__name__)


def sentry_task(func):
    """
    Wrapper for Django-Q tasks so that Sentry logging
    doesn't choke on Django-Q internals in the stack trace,
    http://gael-varoquaux.info/programming/decoration-in-python-done-right-decorating-and-pickling.html
    """

    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception:
            # The task always succeeds, never retry.
            if SENTRY_DSN:
                # Try report exception to Sentry
                capture_exception()
            else:
                # Don't try to use Sentry.
                logger.exception("Sentry not enabled - error caught in task.")

    return wrapper
