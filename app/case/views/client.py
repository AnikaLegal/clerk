from django.http import Http404
from rest_framework.decorators import api_view
from rest_framework.response import Response

from case.serializers import ClientDetailSerializer
from core.models import Client, Issue
from case.utils.router import Router
from case.utils.react import render_react_page

from .auth import paralegal_or_better_required

router = Router("client")
router.create_route("detail").uuid("pk")


@router.use_route("detail")
@paralegal_or_better_required
@api_view(["GET", "POST"])
def client_detail_view(request, pk):
    try:
        client = Client.objects.prefetch_related("issue_set").get(pk=pk)
        if request.user.is_paralegal:
            is_assigned = Issue.objects.filter(
                client=client, paralegal=request.user
            ).exists()
            if not is_assigned:
                # Not allowed
                raise Http404()
    except Client.DoesNotExist:
        raise Http404()

    if request.method == "GET":
        name = client.get_full_name()
        context = {"client": ClientDetailSerializer(client).data}
        return render_react_page(request, f"Client {name}", "client-detail", context)
    elif request.method == "POST":

        serializer = ClientDetailSerializer(instance=client, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({"client": serializer.data})
