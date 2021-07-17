from django.http import HttpResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt


@csrf_exempt
@require_http_methods(["POST"])
def receive_email_view(request):
    """


    https://docs.sendgrid.com/for-developers/parsing-email/setting-up-the-inbound-parse-webhook#default-parameters
    from: the sender of the email
    to: the recipient(s) of the email
    subject: the email subject
    text the email body in plaintext format
    html the email body in HTML format

    ngrok http 5000
    https://app.sendgrid.com/settings/parse


    """
    post_data = request.POST
    print("From:", post_data["from"])
    print("To:", post_data["to"])
    print("Subject:", post_data["subject"])
    print("Body:", post_data["text"])
    return HttpResponse(200)
