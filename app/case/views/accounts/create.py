from django.views.decorators.http import require_http_methods
from django.shortcuts import render, redirect

from case.views.auth import coordinator_or_better_required
from case.utils.router import Route
from case.forms import InviteParalegalForm
from case.utils import merge_form_data

create_route = Route("create").path("invite")


@create_route
@require_http_methods(["GET", "POST"])
@coordinator_or_better_required
def account_detail_view(request):
    if request.method == "POST":
        default_data = {"username": request.POST.get("email")}
        data = merge_form_data(request.POST, default_data)
        form = InviteParalegalForm(data)
        if form.is_valid():
            user = form.save()
            return redirect("account-detail", user.pk)
    else:
        form = InviteParalegalForm()

    context = {"form": form}
    return render(request, "case/accounts/create.html", context)
