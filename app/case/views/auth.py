from urllib.parse import urlparse

from django.conf import settings
from django.contrib.auth import REDIRECT_FIELD_NAME
from django.contrib.auth.views import redirect_to_login
from django.core.exceptions import PermissionDenied
from django.shortcuts import resolve_url
from rest_framework import permissions


def login_required(view):
    """
    User must be logged in to view this page.
    """

    def view_wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return _redirect_to_login(request)

        return view(request, *args, **kwargs)

    return view_wrapper


def paralegal_or_better_required(view):
    """
    User must be a paralegal or better to view this page.
    """

    def view_wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return _redirect_to_login(request)

        if not request.user.is_paralegal_or_better:
            raise PermissionDenied

        return view(request, *args, **kwargs)

    return view_wrapper


def coordinator_or_better_required(view):
    """
    User must be a coordinator or better to view this page.
    """

    def view_wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return _redirect_to_login(request)

        if not request.user.is_coordinator_or_better:
            raise PermissionDenied

        return view(request, *args, **kwargs)

    return view_wrapper


def admin_or_better_required(view):
    """
    User must be an admin or better to view this page.
    """

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


class ParalegalOrBetterObjectPermission(permissions.IsAuthenticated):
    def has_permission(self, request, view):
        return (
            super().has_permission(request, view)
            and request.user.is_paralegal_or_better
        )

    def has_object_permission(self, request, view, obj):
        """
        By convention models with special permissions will provide a
        custom `check_permission` method, which takes an annotated user.
        """
        if hasattr(obj, "check_permission"):
            # Otherwise you need object permisisons.
            return obj.check_permission(request.user)
        else:
            # If there are no object level permissions, assume object level access.
            return True


class CoordinatorOrBetterPermission(permissions.IsAuthenticated):
    """
    Coordinators or better required.
    """

    def has_permission(self, request, view):
        return (
            super().has_permission(request, view)
            and request.user.is_coordinator_or_better
        )

    def has_object_permission(self, request, view, obj):
        return self.has_permission(request, view)


class CoordinatorOrBetterCanWritePermission(permissions.IsAuthenticated):
    """
    Coordinators or better can write, any paralegal.
    """

    def has_permission(self, request, view):
        has_permission = super().has_permission(request, view)
        if request.method in permissions.SAFE_METHODS:
            return has_permission and request.user.is_paralegal_or_better
        else:
            return has_permission and request.user.is_coordinator_or_better

    def has_object_permission(self, request, view, obj):
        return self.has_permission(request, view)


# TODO: remove?
class LawyerOrBetterPermission(permissions.IsAuthenticated):
    """
    Lawyer or better required.
    """

    def has_permission(self, request, view):
        return (
            super().has_permission(request, view) and request.user.is_lawyer_or_better
        )

    def has_object_permission(self, request, view, obj):
        return self.has_permission(request, view)
