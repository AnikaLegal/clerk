from django.db.models import Q
from rest_framework.response import Response
from rest_framework.decorators import api_view
from django.urls import reverse

from accounts.models import User
from case.serializers import UserSerializer
from case.views.auth import coordinator_or_better_required
from case.utils.router import Route
from case.utils.react import render_react_page, is_react_api_call

list_route = Route("list")


@list_route
@api_view(["GET"])
@coordinator_or_better_required
def account_list_view(request):
    users = User.objects.prefetch_related("groups").order_by("-date_joined").all()
    if "name" in request.GET or "group" in request.GET:
        name, group = request.GET.get("name"), request.GET.get("group")
        query = None
        if name:
            query = Q(first_name__icontains=name) | Q(last_name__icontains=name)

        if group:
            group_query = Q(groups__name=group)
            query = (query & group_query) if query else group_query

        if query:
            users = users.filter(query)

    context = {
        "users": UserSerializer(users, many=True).data,
        "create_url": reverse("account-create"),
    }
    if is_react_api_call(request):
        return Response(data=context["users"])
    else:
        return render_react_page(request, "Accounts", "accounts-list", context)
