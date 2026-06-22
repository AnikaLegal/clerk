from case.utils import render_react_page
from django.core import exceptions as django_exceptions
from django.http import Http404
from drf_standardized_errors.handler import exception_handler
from rest_framework import exceptions as drf_exceptions


def custom_exception_handler(exception, context):
    """
    Custom DRF exception handler.

    Renders React 403/404 pages for non-API ``/clerk/`` routes, otherwise
    delegates to drf-standardized-errors so API responses share a single,
    predictable error envelope.
    """
    request = context.get("request")
    if (
        request
        and request.path.startswith("/clerk/")
        and not request.path.startswith("/clerk/api/")
    ):
        if isinstance(exception, django_exceptions.PermissionDenied) or isinstance(
            exception, drf_exceptions.PermissionDenied
        ):
            return render_react_page(request, "Not Allowed", "403", {}, status=403)
        if isinstance(exception, Http404) or isinstance(
            exception, drf_exceptions.NotFound
        ):
            return render_react_page(request, "Not Found", "404", {}, status=404)

    return exception_handler(exception, context)
