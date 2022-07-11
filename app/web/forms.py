from django import forms

from webhooks.models import WebflowContact
from web.models import ContentFeeback
from emails.models import NoEmail


class ContactForm(forms.ModelForm):
    class Meta:
        model = WebflowContact
        fields = [
            "name",
            "email",
            "phone",
            "referral",
        ]


class ContentFeebackForm(forms.ModelForm):
    class Meta:
        model = ContentFeeback
        fields = ["score", "reason", "name", "email", "page"]

class NoEmailForm(forms.ModelForm):
    class Meta:
        model = NoEmail
        fields = (
            "id",
            "name",
            "phone_number",
        )
