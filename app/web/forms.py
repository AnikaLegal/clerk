from django import forms

from webhooks.models import WebflowContact
from web.models import ContentFeedback


class ContactForm(forms.ModelForm):
    class Meta:
        model = WebflowContact
        fields = [
            "name",
            "email",
            "phone",
            "referral",
        ]


class ContentFeedbackForm(forms.ModelForm):
    class Meta:
        model = ContentFeedback
        fields = ["score", "reason", "name", "email", "page"]
