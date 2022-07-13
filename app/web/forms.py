from django import forms

from webhooks.models import WebflowContact
from web.models import ContentFeeback


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
