import json
import logging

from rest_framework.decorators import api_view
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from django.conf import settings

from emails.models import Email, EmailState
from .models import JotformSubmission, WebflowContact
from .serializers import NoEmailSerializer

logger = logging.getLogger(__file__)


@api_view(["POST"])
def intake_no_email_view(request):
    """
    For when a intake form user has no email but wants to contact us.
    """
    serializer = NoEmailSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    name = serializer.validated_data["name"]
    phone = serializer.validated_data["phone_number"]
    email_data = {
        "from_address": settings.DEFAULT_FROM_EMAIL,
        "to_address": settings.INTAKE_NOEMAIL_EMAIL,
        "subject": f"Intake submitted with no email address [{name}]",
        "state": EmailState.READY_TO_SEND,
        "text": f"{name} tried to complete the intake form but they have no email. Their phone number is {phone}",
    }
    logger.info("Received no-email intake submission %s", email_data)
    if settings.INTAKE_NOEMAIL_EMAIL:
        Email.objects.create(**email_data)

    return Response({}, status=200)


@api_view(["POST"])
def webflow_form_view(request):
    """
    Save data from webflow form submission.
    Can't use DRF serializers here because the form names are ugly as fuck.

    By the way this is super insecure and you can spam the shit out of this using curl from anywhere.
    curl \
        --header "Content-Type: application/json" \
        --request POST  \
        --data '{"data": {"Name": "Matt", "Email": "matt@foo.com", "Phone Number": "11111", "Referral": "Foobar"}}' \
        http://localhost:8000/api/webhooks/webflow-form/

    But don't because it'd be a shitty thing to do.
    """
    try:
        data = request.data["data"]
        model_kwargs = {
            "name": data["Name"],
            "email": data["Email"],
            "phone": data["Phone Number"],
            "referral": data["Referral"],
        }
    except KeyError:
        raise ValidationError("Invalid request format.")

    WebflowContact.objects.create(**model_kwargs)
    return Response({"message": "We got the form. :)"}, status=201)


@api_view(["POST"])
def jotform_form_view(request):
    """
    Save Jotform data from a POST request
    """
    try:
        data = request.data["rawRequest"]
        model_kwargs = {
            "form_name": request.data["formTitle"],
            "answers": json.loads(data),
        }
    except KeyError:
        raise ValidationError("Invalid request format.")

    JotformSubmission.objects.create(**model_kwargs)
    return Response({"message": "Received Jotform submission."}, status=201)
