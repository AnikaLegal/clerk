import logging
import json

from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from rest_framework.decorators import api_view

from .models import WebflowContact, JotformSubmission

logger = logging.getLogger(__file__)


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
        model_kwargs = {"form_name": request.data["formTitle"], "answers": json.loads(data)}
    except KeyError:
        raise ValidationError("Invalid request format.")

    JotformSubmission.objects.create(**model_kwargs)
    return Response({"message": "Received Jotform submission."}, status=201)
