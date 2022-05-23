from django.views.decorators.http import require_http_methods
from django.http import Http404

from case.serializers import ClientDetailSerializer
from core.models import Client, Issue
from .auth import paralegal_or_better_required
from case.utils.router import Router
from case.utils.react import render_react_page
from rest_framework.decorators import api_view


router = Router("client")
router.create_route("detail").uuid("pk")


@router.use_route("detail")
@paralegal_or_better_required
@require_http_methods(["GET", "POST"])
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

    name = client.get_full_name()
    context = {"client": ClientDetailSerializer(client).data}
    return render_react_page(request, f"Client {name}", "client-detail", context)


# CLIENT_DETAIL_FORMS = {
#     "contact": ClientContactDynamicForm,
#     "personal": ClientPersonalDynamicForm,
#     "misc": ClientMiscDynamicForm,
# }
# @router.use_route("detail")
# @paralegal_or_better_required
# @require_http_methods(["GET", "POST"])
# def client_detail_view(request, pk, form_slug: str = ""):
#     try:
#         client = Client.objects.prefetch_related("issue_set").get(pk=pk)
#         if request.user.is_paralegal:
#             is_assigned = Issue.objects.filter(
#                 client=client, paralegal=request.user
#             ).exists()
#             if not is_assigned:
#                 # Not allowed
#                 raise Http404()

#     except Client.DoesNotExist:
#         raise Http404()

#     forms = DynamicTableForm.build_forms(
#         request, form_slug, client, CLIENT_DETAIL_FORMS
#     )
#     context = {"client": client, "forms": forms}
#     form_resp = DynamicTableForm.get_response(request, form_slug, forms, context)
#     if form_resp:
#         return form_resp
#     else:
#         return render(request, "case/client_detail.html", context)
