from django.http import HttpResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt

from .service import process_inbound_email


@csrf_exempt
@require_http_methods(["POST"])
def receive_email_view(request):
    """
    Receive an inbound email from SendGrid, parse and save to database.
    SendGrid will retry email send if 2xx status code is not returned.

    See docs/emails.md for more details.
    """
    process_inbound_email(request.POST, request.FILES)
    return HttpResponse(200)
