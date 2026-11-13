from django.conf import settings
from django.contrib import admin
from django.core.exceptions import PermissionDenied
from django.shortcuts import redirect, resolve_url


class ClerkAdminSite(admin.AdminSite):
    site_header = f"Anika Clerk {settings.ADMIN_PREFIX} Admin".title()
    site_title = "Anika Clerk"
    index_title = f"{settings.ADMIN_PREFIX} Admin".title()

    def login(self, request, extra_context=None):
        if settings.PASSWORD_LOGIN_ENABLED:
            return super().login(request, extra_context)
        if request.user.is_authenticated:
            # Signed in but not staff. The Clerk login would send them
            # straight back here.
            raise PermissionDenied
        # Send people to the Clerk Google login, keeping ?next= so they come
        # back here afterwards.
        login_url = resolve_url(settings.LOGIN_URL)
        query = request.GET.urlencode()
        return redirect(f"{login_url}?{query}" if query else login_url)
