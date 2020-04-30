import logging

from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from rest_framework.decorators import api_view

from .models import WebflowContact

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
        --data '{"data": {"name": "Matt", "email": "matt@foo.com", "phone": "11111"}}' \
        http://localhost:8000/api/webhooks/webflow-form/

    But don't because it'd be a shitty thing to do.
    """
    try:
        data = request.data["data"]
        model_kwargs = {"name": data["Name"], "email": data["Email"], "phone": data["Phone Number"]}
    except KeyError:
        raise ValidationError("Invalid request format.")

    WebflowContact.objects.create(**model_kwargs)
    return Response({"message": "We got the form. :)"}, status=201)
