import logging

from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from django.views.decorators.http import require_http_methods
from rest_framework.decorators import api_view

from emails.service import save_inbound_email
from emails.models import Email, EmailState

logger = logging.getLogger(__name__)


@csrf_exempt
@require_http_methods(["POST"])
def receive_email_view(request):
    """
    Receive an inbound email from SendGrid, parse and save to database.
    SendGrid will retry email send if 2xx status code is not returned.

    See docs/emails.md for more details.
    """
    save_inbound_email(request.POST, request.FILES)
    return HttpResponse(200)


EMAIL_EVENTS = ["delivered", "processed", "bounce", "dropped", "spamreport"]


@csrf_exempt
@api_view(["POST"])
def events_email_view(request):
    """
    Receive an events update from Sendgrid.

    See docs/emails.md for more details.
    """
    events = request.data
    for event in events:
        to_email = event["email"]
        timestamp = event["timestamp"]
        sendgrid_id = event["sg_message_id"]
        event_type = event["event"]
        if event_type not in EMAIL_EVENTS:
            logger.info(
                "Skipping email event %s for email with sendgrid ID %s",
                event_type,
                sendgrid_id,
            )
            continue

        email = find_email(to_email, timestamp, sendgrid_id)
        if not email:
            logger.info(
                "Could not find email email for event %s at %s with sendgrid ID %s",
                event_type,
                timestamp,
                sendgrid_id,
            )
        else:
            logger.info(
                "Marking Email<%s> as %s with sendgrid ID %s",
                email.id,
                event_type,
                sendgrid_id,
            )
            is_id_match = not email.sendgrid_id or email.sendgrid_id == sendgrid_id
            assert is_id_match, "Sendgrid ID mismatch."
            if event_type == "delivered":
                email.state = EmailState.DELIVERED
            elif event_type in ["bounce", "dropped", "spamreport"]:
                email.state = EmailState.DELIVERY_FAILURE

            email.sendgrid_id = sendgrid_id
            email.save()

    return HttpResponse(200)


def find_email(to_email, timestamp, sendgrid_id):
    email = None
    try:
        email = Email.objects.get(sendgrid_id=sendgrid_id)
    except Email.DoesNotExist:
        logger.info("Could not find email with sendgrid ID %s", sendgrid_id)

    if not email:
        event_at = timezone.datetime.fromtimestamp(timestamp, tz=timezone.utc)
        before = event_at - timezone.timedelta(seconds=30)
        after = event_at + timezone.timedelta(seconds=30)
        try:
            email = Email.objects.get(
                to_address=to_email, processed_at__gte=before, processed_at__lte=after
            )
        except Email.DoesNotExist:
            logger.error(
                "Could not find email to %s at %s for sendgrid ID %s",
                to_email,
                timestamp,
                sendgrid_id,
            )
        except Email.MultipleObjectsReturned:
            logger.error(
                "Found multiple emails to %s at %s for sendgrid ID %s",
                to_email,
                timestamp,
                sendgrid_id,
            )

    return email
