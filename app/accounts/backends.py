from django.conf import settings
from django.contrib.auth.backends import ModelBackend


class PermissionsBackend(ModelBackend):
    """
    ModelBackend's user lookup and permission checks, with password login only
    where PASSWORD_LOGIN_ENABLED allows it. Everyone else signs in with Google.
    """

    def authenticate(self, request, username=None, password=None, **kwargs):
        if not settings.PASSWORD_LOGIN_ENABLED:
            return None
        return super().authenticate(request, username, password, **kwargs)
