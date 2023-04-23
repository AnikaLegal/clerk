from django.views.decorators.http import require_http_methods
from intake.utils import render_react_page


@require_http_methods(["GET"])
def intake_view(request):
    """Intake form"""
    return render_react_page(request, "Client intake", "intake-landing", {})
