from twilio.twiml.voice_response import VoiceResponse, Say


def say_christmas_message(resp: VoiceResponse):
    say = Say("Thank you for calling Anika Legal", voice="Polly.Nicole")
    say.p(
        "We are closed for the holiday season from 20 December 2022, and reopening on 9 January 2023."
    )
    say.p(
        "If you require urgent legal assistance, please contact Victoria Legal Aid on 1 3 0 0 7 9 2 3 8 7"
    )
    say.p("From the entire team at Anika Legal, we hope you have a safe holiday season")
    resp.append(say)
