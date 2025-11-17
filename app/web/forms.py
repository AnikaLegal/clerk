from django import forms

from webhooks.models import WebflowContact
from web.models import ContentFeedback, DocumentLog
from web.models.document import StateChoices, SectorChoices, ReferrerChoices


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


class DocumentLogForm(forms.ModelForm):
    class Meta:
        model = DocumentLog
        fields = [
            "state",
            "sector",
            "referrer",
        ]

    state = forms.ChoiceField(
        choices=[("", "Where are you located?")] + list(StateChoices.choices),
        required=True,
    )
    sector = forms.ChoiceField(
        choices=[("", "What sector do you work in?")] + list(SectorChoices.choices),
        required=True,
    )
    referrer = forms.ChoiceField(
        choices=[("", "Where did you hear about this report?")]
        + list(ReferrerChoices.choices),
        required=True,
    )
