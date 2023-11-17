from urllib.parse import urljoin

from django.conf import settings
from django.http import HttpResponse
from django.urls import reverse
from django.views.decorators.http import require_http_methods
from twilio.rest import Client
from twilio.base.exceptions import TwilioRestException
from twilio.twiml.messaging_response import MessagingResponse
from twilio.twiml.voice_response import Gather, VoiceResponse

from core.models.issue import CaseTopic
from caller.choices import Choice
from caller.messages import sms, voice

from .models import Call

# Greet user, introduce Anika, explain options.
CALL_INTRO_AUDIO = "call-intro.wav"
# Response when user selects repairs option.
OPTION_REPAIRS_AUDIO = "option-repairs.wav"
# Response when user selects bonds option.
OPTION_BONDS_AUDIO = "option-bonds.wav"
# Response when user selects callback option.
OPTION_CALLBACK_AUDIO = "option-callback.wav"
# Response when user no option and the input times out.
CALL_TIMEOUT_AUDIO = "call-timeout.wav"

TOPIC_MAPPING = {
    Choice.REPAIRS: CaseTopic.REPAIRS,
    Choice.BONDS: CaseTopic.BONDS,
    Choice.CALLBACK: CaseTopic.OTHER,
}

@require_http_methods(["GET"])
def christmas_answer_view(request):  # Used for christmas
    """Respond to phone call from user"""
    response = VoiceResponse()
    response.play(_get_audio_url("christmas-office-closed.wav"))
    return TwimlResponse(response)


@require_http_methods(["GET"])
def answer_view(request):  # Normal view
    """Respond to phone call from user"""
    response = VoiceResponse()

    # Create an entry for this new call.
    number = request.GET.get("From")
    call = Call(phone_number=number)
    call.save()

    # Play message and record user's choice.
    gather = Gather(
        action="/caller/collect/", numDigits=1, method="GET", timeout=10, enhanced=True
    )
    gather.play(_get_audio_url(CALL_INTRO_AUDIO))
    response.append(gather)

    # End the call if user doesn't give us anything.
    response.play(_get_audio_url(CALL_TIMEOUT_AUDIO))
    return TwimlResponse(response)


@require_http_methods(["GET"])
def collect_view(request):
    """Handle phone call where user makes a choice"""
    response = VoiceResponse()

    # Retrieve user's number and choice.
    number = request.GET.get("From")
    choice = request.GET.get("Digits")

    # Generate message depending on user choice.
    if choice == Choice.REPAIRS:
        audio_url = _get_audio_url(OPTION_REPAIRS_AUDIO)
        message_text = sms.REPAIRS_SMS_MESSAGE
    elif choice == Choice.BONDS:
        audio_url = _get_audio_url(OPTION_BONDS_AUDIO)
        message_text = sms.BONDS_SMS_MESSAGE
    elif choice == Choice.CALLBACK:
        audio_url = _get_audio_url(OPTION_CALLBACK_AUDIO)
        message_text = sms.CALLBACK_SMS_MESSAGE
    else: # Repeat options.
        response.redirect = response.redirect(reverse("caller-answer"), method="GET")
        return TwimlResponse(response)

    # Send an SMS for valid choices.
    client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)

    try:
        client.messages.create(
            to=number, from_=settings.TWILIO_PHONE_NUMBER, body=message_text
        )
    except TwilioRestException:
        pass  # It's not a mobile number

    response.play(audio_url)

    # Retrieve and update corresponding entry for valid choices.
    call = Call.objects.filter(phone_number=number).order_by("-created_at").first()
    call.topic = TOPIC_MAPPING[choice]
    call.requires_callback = choice == Choice.CALLBACK
    call.save()

    return TwimlResponse(response)


@require_http_methods(["GET"])
def message_view(request):
    """Respond to SMS from user"""
    response = MessagingResponse()
    response.message(sms.INBOUND_SMS_REPLY_MESSAGE)
    return TwimlResponse(response)


class TwimlResponse(HttpResponse):
    """HTTP response returning Twilio Markup Language (TwiML)"""

    def __init__(self, twiml_obj, **kwargs):
        super_kwargs = {"status": 200, "content_type": "application/xml", **kwargs}
        return super().__init__(str(twiml_obj), **super_kwargs)


def _get_audio_url(filename: str):
    return urljoin(settings.TWILIO_AUDIO_BASE_URL, filename)
