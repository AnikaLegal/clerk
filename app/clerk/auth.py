# Disable CSRF
# FIXME: Remove this once users can log in and fetch a token - or if you figure out a smarter way to do this.
from rest_framework.authentication import SessionAuthentication


class CsrfExemptSessionAuthentication(SessionAuthentication):
    def enforce_csrf(self, request):
        return False
