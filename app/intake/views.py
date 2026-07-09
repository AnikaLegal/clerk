from django.views.decorators.csrf import ensure_csrf_cookie
from django.views.decorators.http import require_http_methods

from intake.utils import render_intake_page


@require_http_methods(["GET", "HEAD"])
@ensure_csrf_cookie
def intake_view(request):
    """
    Public client intake form (SurveyJS single page app).

    ensure_csrf_cookie so that logged-in staff filling out the form can send
    the CSRF token that SessionAuthentication demands of them: anonymous
    visitors POST without CSRF, session-authenticated users may not.
    """
    return render_intake_page(request, title="Get free help")
