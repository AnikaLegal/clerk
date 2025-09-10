import logging

from django.db import transaction
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from emails.models import Email, EmailState
from emails.service import save_inbound_email
from rest_framework.decorators import api_view


logger = logging.getLogger(__name__)


@csrf_exempt
@require_http_methods(["POST"])
def receive_email_view(request):
    """
    Receive an inbound email from SendGrid and save to database. SendGrid will
    retry email send if 2xx status code is not returned.

    Some ESPs impose strict time limits on webhooks, and will consider them
    failed if they don't respond within a certain timeframe, so we save the
    email and attachments synchronously and then process the received email
    asynchronously.

    See docs/emails.md for more details.
    """
    save_inbound_email(request.POST, request.FILES)
    return HttpResponse(200)


EMAIL_EVENTS = ["delivered", "bounce", "dropped"]


@csrf_exempt
@api_view(["POST"])
def events_email_view(request):
    """
    Receive an events update from Sendgrid. See docs/emails.md for more details.
    """
    for event in request.data:
        event_type = event["event"]
        timestamp = event["timestamp"]

        # Get the first part of the sg_message_id, if any.
        sendgrid_id = None
        sg_message_id = event.get("sg_message_id")
        if sg_message_id:
            sendgrid_id = sg_message_id.split(".")[0]

        if not sendgrid_id:
            logger.info(
                f"Could not get sendgrid_id for event '{event_type}' at {timestamp}"
            )
            continue

        if event_type not in EMAIL_EVENTS:
            logger.info(
                f"Skipping email event '{event_type}' for email with sendgrid id {sendgrid_id}"
            )
            continue

        with transaction.atomic():
            # Try find the email based on the sendgrid message ID.
            try:
                email = Email.objects.select_for_update().get(sendgrid_id=sendgrid_id)
            except Email.DoesNotExist:
                logger.info(
                    f"Could not find email for event '{event_type}' with sendgrid id {sendgrid_id}"
                )
                continue

            logger.info(
                f"Updating Email<{email.pk}> for event '{event_type}' with sendgrid id {sendgrid_id}"
            )
            state = None
            if event_type == "delivered":
                state = EmailState.DELIVERED
            elif event_type in ["bounce", "dropped"]:
                state = EmailState.DELIVERY_FAILURE

            # Skip if the email state is already the same.
            if state and email.state != state:
                logger.info(f"Setting Email<{email.pk}> state to '{state}'")
                email.state = state
                email.save()

    return HttpResponse(200)
