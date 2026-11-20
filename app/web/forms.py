from django import forms
from django_recaptcha.fields import ReCaptchaField
from django_recaptcha.widgets import ReCaptchaV3

from enquiry.models import Enquiry, EnquirySource
from web.fields import HtmxReCaptchaV3Field
from web.models import ContentFeedback, DocumentLog
from web.models.document import ReferrerChoices, SectorChoices, StateChoices


class ContactForm(forms.ModelForm):
    class Meta:
        model = Enquiry
        fields = [
            "name",
            "email",
            "phone",
            "captcha",
        ]

    captcha = HtmxReCaptchaV3Field(action="contact")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in ("name", "email", "phone"):
            self.fields[field].required = True

    def save(self, commit=True):
        self.instance.source = EnquirySource.CONTACT_FORM
        self.instance.requires_callback = True
        return super().save(commit)


class ContentFeedbackForm(forms.ModelForm):
    class Meta:
        model = ContentFeedback
        fields = [
            "score",
            "reason",
            "name",
            "email",
            "page",
            "captcha",
        ]

    captcha = HtmxReCaptchaV3Field(action="feedback")


class DocumentLogForm(forms.ModelForm):
    class Meta:
        model = DocumentLog
        fields = [
            "state",
            "sector",
            "referrer",
            "captcha",
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
    captcha = ReCaptchaField(widget=ReCaptchaV3(action="document_log"))
