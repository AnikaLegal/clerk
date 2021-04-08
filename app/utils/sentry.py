import os

from sentry_sdk import capture_exception

SENTRY_DSN = os.environ.get("RAVEN_DSN")


class WithSentryCapture:
    """
    Wrapper for Django-Q tasks so that Sentry logging doesn't choke on
    Django-Q internals in the stack trace,

    Written as a class so it is pickleable, as per
    http://gael-varoquaux.info/programming/decoration-in-python-done-right-decorating-and-pickling.html
    """

    def __init__(self, func):
        self.func = func

    def __call__(self, *args, **kwargs):
        if SENTRY_DSN:
            # Try report exception to Sentry
            try:
                return self.func(*args, **kwargs)
            except Exception:
                capture_exception()
                raise
        else:
            # Don't try use Sentry
            return self.func(*args, **kwargs)

    def __str__(self):
        return f"SentryCapture{self.func}"
