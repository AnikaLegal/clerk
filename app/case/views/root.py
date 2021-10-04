from django.shortcuts import redirect, render
from django.views.decorators.http import require_http_methods

from case.views.auth import login_required


@require_http_methods(["GET"])
def root_view(request):
    return redirect("case-list")


@login_required
@require_http_methods(["GET"])
def not_allowed_view(request):
    return render(request, "case/not_allowed.html")
