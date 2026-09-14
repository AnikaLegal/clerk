from case.utils import render_react_page
from django.conf import settings
from django.db import DatabaseError, connection
from django.http import HttpResponse
from django.views import defaults


def custom_403_handler(request, exception):
    if request.path.startswith("/clerk/"):
        return render_react_page(request, "Not Allowed", "403", {}, status=403)
    else:
        return defaults.permission_denied(request, exception)


def custom_404_handler(request, exception):
    # Note: let it fall through to default 404 in debug mode so the URLConf is
    # displayed for easier debugging.
    if request.path.startswith("/clerk/") and not settings.DEBUG:
        return render_react_page(request, "Not Found", "404", {}, status=404)
    else:
        return defaults.page_not_found(request, exception)


def health_view(request):
    """
    Liveness check for the container orchestrator: OK only if the database can
    be reached. Deliberately cheap and independent of site content.
    """
    try:
        connection.ensure_connection()
    except DatabaseError:
        return HttpResponse(
            "database unavailable", status=503, content_type="text/plain"
        )
    return HttpResponse("ok", content_type="text/plain")
