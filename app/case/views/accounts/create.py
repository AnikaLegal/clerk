from django.views.decorators.http import require_http_methods
from django.shortcuts import render, redirect
from django_q.tasks import async_task

from accounts.models import User
from case.views.auth import coordinator_or_better_required
from case.utils.router import Route
from case.forms import InviteParalegalForm
from case.utils import merge_form_data
from microsoft.tasks import set_up_new_user_task

create_route = Route("create").path("invite")


@create_route
@require_http_methods(["GET", "POST"])
@coordinator_or_better_required
def account_detail_view(request):
    if request.method == "POST":
        email = request.POST.get("email")

        # Is this User already in Clerk?
        existing_user = User.objects.get(email=email)

        if existing_user and email.endswith("@anikalegal.com"):
            async_task(set_up_new_user_task, existing_user.pk)
            return redirect("account-detail", existing_user.pk)
        else:
            data = merge_form_data(request.POST, {"username": email})
            form = InviteParalegalForm(data)
            if form.is_valid():
                user = form.save()
                return redirect("account-detail", user.pk)
    else:
        context = {"form": InviteParalegalForm()}
        return render(request, "case/accounts/create.html", context)
