from urllib.parse import urlparse

from django.shortcuts import resolve_url
from django.conf import settings
from django.contrib.auth import REDIRECT_FIELD_NAME
from django.contrib.auth.views import redirect_to_login
from django.core.exceptions import PermissionDenied


def paralegal_or_better_required(view):
    def view_wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return _redirect_to_login(request)

        if not request.user.is_paralegal_or_better:
            raise PermissionDenied

        return view(request, *args, **kwargs)

    return view_wrapper


def coordinator_or_better_required(view):
    def view_wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return _redirect_to_login(request)

        if not request.user.is_coordinator_or_better:
            raise PermissionDenied

        return view(request, *args, **kwargs)

    return view_wrapper


def admin_or_better_required(view):
    def view_wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return _redirect_to_login(request)

        if not request.user.is_admin_or_better:
            raise PermissionDenied

        return view(request, *args, **kwargs)

    return view_wrapper


def _redirect_to_login(request):
    """See decorator: django.contrib.auth.decorators.user_passes_test"""
    path = request.build_absolute_uri()
    resolved_login_url = resolve_url(settings.LOGIN_URL)
    if _is_not_infinite_redirect(path, resolved_login_url):
        path = request.get_full_path()
        return redirect_to_login(path, resolved_login_url, REDIRECT_FIELD_NAME)


def _is_not_infinite_redirect(path, resolved_login_url):
    login_scheme, login_netloc = urlparse(resolved_login_url)[:2]
    current_scheme, current_netloc = urlparse(path)[:2]
    return (not login_scheme or login_scheme == current_scheme) and (
        not login_netloc or login_netloc == current_netloc
    )
