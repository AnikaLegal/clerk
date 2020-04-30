import logging

from rest_framework.response import Response
from rest_framework.decorators import api_view

logger = logging.getLogger(__file__)


@api_view(["POST"])
def webflow_form_view(request):
    logger.info("Received Webflow webhook data: %s", request.data)
    return Response({"message": "We got the form. :)"})
