from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.views.decorators.http import require_http_methods
from django.http import Http404

# from case.forms import ClientForm
from core.models import Client

from django.contrib.auth.decorators import user_passes_test
from .auth import is_superuser


# FIXME: Permissions
@login_required
@user_passes_test(is_superuser, login_url="/")
@require_http_methods(["GET"])
def client_detail_view(request, pk):
    try:
        # FIXME: Who has access to this?
        client = Client.objects.prefetch_related("issue_set").get(pk=pk)
    except Client.DoesNotExist:
        raise Http404()

    context = {"client": client}
    return render(request, "case/client_detail.html", context)
