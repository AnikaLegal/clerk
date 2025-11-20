from django_recaptcha.fields import ReCaptchaField
from django_recaptcha.widgets import ReCaptchaV3


class HtmxReCaptchaV3Widget(ReCaptchaV3):
    template_name = "web/htmx/_recaptcha_v3.html"


class HtmxReCaptchaV3Field(ReCaptchaField):
    def __init__(self, *args, **kwargs):
        kwargs["widget"] = HtmxReCaptchaV3Widget(action=kwargs.pop("action", None))
        super().__init__(*args, **kwargs)
