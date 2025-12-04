from rest_framework.views import exception_handler
from case.utils import render_react_page
from django.http import Http404
from django.core.exceptions import PermissionDenied
from rest_framework import exceptions


def custom_exception_handler(exception, context):
    """
    Custom DRF exception handler.
    """
    request = context.get("request")
    if (
        request
        and request.path.startswith("/clerk/")
        and not request.path.startswith("/clerk/api/")
    ):
        if isinstance(exception, PermissionDenied) or isinstance(
            exception, exceptions.PermissionDenied
        ):
            return render_react_page(request, "Not Allowed", "403", {}, status=403)
        if isinstance(exception, Http404) or isinstance(exception, exceptions.NotFound):
            return render_react_page(request, "Not Found", "404", {}, status=404)

    response = exception_handler(exception, context)
    return response
