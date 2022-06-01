from django.shortcuts import redirect
from django.views.decorators.http import require_http_methods


@require_http_methods(["GET"])
def root_view(request):
    return redirect("case-list")
