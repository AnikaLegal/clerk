from django import forms
from django_recaptcha.fields import ReCaptchaField
from django_recaptcha.widgets import ReCaptchaV3

from webhooks.models import WebflowContact


class IntakeNoEmailForm(forms.ModelForm):
    """
    Contact request from an intake user who has no email address. Collects
    just a name and phone number and feeds the same WebflowContact pipeline
    (blacklist check + Slack callback alert) as the public site's landing
    contact form. reCAPTCHA guards this public, unauthenticated endpoint.
    """

    class Meta:
        model = WebflowContact
        fields = ["name", "phone", "captcha"]

    captcha = ReCaptchaField(widget=ReCaptchaV3(action="intake_noemail"))
