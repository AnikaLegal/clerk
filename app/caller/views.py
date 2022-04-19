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

from .models import Call

# Greet user, introduce Anika, explain options.
CALL_INTRO_AUDIO = "call-intro.wav"
# Response when user selects repairs option.
OPTION_REPAIRS_AUDIO = "option-repairs.wav"
# Response when user selects evictions option.
OPTION_EVICTIONS_AUDIO = "option-evictions.wav"
# Response when user selects evictions option.
OPTION_BONDS_AUDIO = "option-bonds.wav"
# Response when user selects callback option.
OPTION_CALLBACK_AUDIO = "option-callback.wav"
# Response when user no option and the input times out.
CALL_TIMEOUT_AUDIO = "call-timeout.wav"

# The SMS message we send to people who send us SMS's.
# We don't do inbound SMS communications so we ask them to send us an email instead.
INBOUND_SMS_REPLY_MESSAGE = "Thank you for sending us an SMS. Please call us on this number or direct written enquiries to contact@anikalegal.com"


# The SMS message we send to people who are enquiring about repairs.
REPAIRS_SMS_MESSAGE = """
Thank you for enquiring about Anika's rental repairs service.

To get help, please fill in this form: https://intake.anikalegal.com

For more info on Anika's services, please visit https://www.anikalegal.com/services/

If you have any other enquiries you can email us at contact@anikalegal.com
"""

# The SMS message we send to people who are enquiring about evictions.
EVICTIONS_SMS_MESSAGE = """
Thank you for enquiring about Anika's evictions service.

To get help, please fill in this form: https://intake.anikalegal.com

For more info on Anika's services, please visit https://www.anikalegal.com/services/

If you have any other enquiries you can email us at contact@anikalegal.com
"""


# The SMS message we send to people who are enquiring about bonds.
BONDS_SMS_MESSAGE = """
Thank you for enquiring about Anika's bonds service.

To get help, please fill in this form: https://intake.anikalegal.com

For more info on Anika's services, please visit https://www.anikalegal.com/services/

If you have any other enquiries you can email us at contact@anikalegal.com
"""


# The SMS message we send to people who want a callback about another issue.
CALLBACK_SMS_MESSAGE = """
Thank you for contacting us about your enquiry, one of our staff will call you in the next 3 business days.

In the meantime, for more info on Anika's services, please visit https://www.anikalegal.com/services/

If you have any other enquiries you can email us at contact@anikalegal.com
"""


TOPIC_MAPPING = {
    "1": CaseTopic.REPAIRS,
    "2": CaseTopic.BONDS,
    "3": CaseTopic.EVICTION,
    "4": CaseTopic.OTHER,
}


@require_http_methods(["GET"])
def answer_view(request):
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
    if choice == "1":
        # Repairs option.
        audio_url = _get_audio_url(OPTION_REPAIRS_AUDIO)
        message_text = REPAIRS_SMS_MESSAGE
    elif choice == "2":
        # Bonds option.
        audio_url = _get_audio_url(OPTION_BONDS_AUDIO)
        message_text = BONDS_SMS_MESSAGE
    elif choice == "3":
        # Evictions option.
        audio_url = _get_audio_url(OPTION_EVICTIONS_AUDIO)
        message_text = EVICTIONS_SMS_MESSAGE
    elif choice == "4":
        audio_url = _get_audio_url(OPTION_CALLBACK_AUDIO)
        message_text = CALLBACK_SMS_MESSAGE
    else:
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
    call.requires_callback = choice == "4"
    call.save()

    return TwimlResponse(response)


@require_http_methods(["GET"])
def message_view(request):
    """Respond to SMS from user"""
    response = MessagingResponse()
    response.message(INBOUND_SMS_REPLY_MESSAGE)
    return TwimlResponse(response)


class TwimlResponse(HttpResponse):
    """HTTP response returning Twilio Markup Language (TwiML)"""

    def __init__(self, twiml_obj, **kwargs):
        super_kwargs = {"status": 200, "content_type": "application/xml", **kwargs}
        return super().__init__(str(twiml_obj), **super_kwargs)


def _get_audio_url(filename: str):
    return urljoin(settings.TWILIO_AUDIO_BASE_URL, filename)
