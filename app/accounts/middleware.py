from social_core.exceptions import AuthStateForbidden, AuthStateMissing
from social_django.middleware import SocialAuthExceptionMiddleware


class LoginErrorMiddleware(SocialAuthExceptionMiddleware):
    """
    Sends failed Google logins back to the login page with a message.
    The OAuth state errors come from a stale or replayed Google callback
    (back button, old tab, expired session), so retrying fixes them.
    """

    def get_message(self, request, exception):
        if isinstance(exception, (AuthStateMissing, AuthStateForbidden)):
            return "Your login session expired. Please log in again."

        return super().get_message(request, exception)
