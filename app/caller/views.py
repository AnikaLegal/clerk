from django.conf import settings
from django.http import HttpResponse
from django.views.decorators.http import require_http_methods
from twilio.twiml.voice_response import VoiceResponse, Gather
from twilio.twiml.messaging_response import MessagingResponse
from twilio.rest import Client
from .models import Call


@require_http_methods(["GET"])
def answer_view(request):
    """Respond to phone call from user"""
    response = VoiceResponse()

    # Play message and record user's choice.
    gather = Gather(action="/caller/collect", numDigits=1)
    gather.say(
        "Thank you for calling Anika Legal. \
        For information about repairing your rental property, please press 1. \
        For information about negotiating a rent reduction, please press 2. \
        If you have specific enquiry and want us to call you back, please press 3.",
        voice="alice",
        language="en-AU",
    )
    response.append(gather)

    # End the call if user doesn't respond.
    response.say(
        "Sorry we haven't received a response, goodbye.",
        voice="alice",
        language="en-AU",
    )
    return TwimlResponse(response)


@require_http_methods(["GET"])
def collect_view(request):
    """Retrieve information from user's call"""
    response = VoiceResponse()

    # Retrieve caller's number and choice.
    number = request.POST.get("From")
    choice = request.POST.get("Digits")

    # Authenticate to send SMS.
    account_sid = settings.TWILIO_ACCOUNT_SID
    auth_token = settings.TWILIO_AUTH_TOKEN
    client = Client(account_sid, auth_token)

    # Generate message depending on user choice.
    if choice == "1":
        message = "Thank you for enquiring about repairing your rental property, \
            please fill in the form at this link: https://test-intake.anikalegal.com/"
    elif choice == "2":
        message = "Thank you for enquiring about reducing your rent, \
            please fill in the form at this link: https://test-intake.anikalegal.com/"
    elif choice == "3":
        message = "Thank you for contacting us about your specific enquiry, \
            one of our staff will call back in the next few days."
    else:
        response.say(
            "Sorry we haven't received a valid choice, please try again.",
            voice="alice",
            language="en-AU",
        )
        response.redirect("/caller/answer", method="POST")
        return TwimlResponse(response)

    # for choices 1 - 3.
    client.messages.create(to=number, from_="+61488839562", body=message)
    response.say(
        "An SMS relating to your enquiry has been sent.",
        voice="alice",
        language="en-AU",
    )
    return TwimlResponse(response)


@require_http_methods(["GET"])
def message_view(request):
    """Respond to SMS from user"""
    response = MessagingResponse()
    response.message(
        "Thank you for sending us an SMS. \
            Please call us on this number or direct written enquiries to contact@anikalegal.com"
    )
    return TwimlResponse(response)


class TwimlResponse(HttpResponse):
    """HTTP response returning Twilio Markup Language (TwiML)"""

    def __init__(self, twiml_obj, **kwargs):
        super_kwargs = {"status": 200, "content_type": "application/xml", **kwargs}
        return super().__init__(str(twiml_obj), **super_kwargs)
