from django.conf import settings
from django.contrib import admin
from django.contrib.auth import REDIRECT_FIELD_NAME
from django.core.exceptions import PermissionDenied
from django.shortcuts import redirect, resolve_url
from django.urls import reverse
from django.utils.http import url_has_allowed_host_and_scheme


class ClerkAdminSite(admin.AdminSite):
    site_header = f"Anika Clerk {settings.ADMIN_PREFIX} Admin".title()
    site_title = "Anika Clerk"
    index_title = f"{settings.ADMIN_PREFIX} Admin".title()

    def login(self, request, extra_context=None):
        if settings.PASSWORD_LOGIN_ENABLED:
            return super().login(request, extra_context)
        if self.has_permission(request):
            next_url = request.GET.get(REDIRECT_FIELD_NAME, "")
            if not url_has_allowed_host_and_scheme(
                next_url,
                allowed_hosts={request.get_host()},
                require_https=request.is_secure(),
            ):
                next_url = reverse("admin:index", current_app=self.name)
            return redirect(next_url)
        if request.user.is_authenticated:
            # Signed in but not staff. The Clerk login would send them
            # straight back here.
            raise PermissionDenied
        # Send people to the Clerk Google login, keeping ?next= so they come
        # back here afterwards.
        login_url = resolve_url(settings.LOGIN_URL)
        query = request.GET.urlencode()
        return redirect(f"{login_url}?{query}" if query else login_url)
