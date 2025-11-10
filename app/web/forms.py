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
        choices=[("", "What state/territory are you from?")]
        + list(StateChoices.choices),
        required=True,
    )
    sector = forms.ChoiceField(
        choices=[("", "What sector are you in?")] + list(SectorChoices.choices),
        required=True,
    )
    referrer = forms.ChoiceField(
        choices=[("", "How did you hear about this report?")]
        + list(ReferrerChoices.choices),
        required=True,
    )
