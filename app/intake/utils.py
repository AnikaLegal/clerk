import json

from django.conf import settings
from django.shortcuts import render


def render_intake_page(request, title, react_context=None):
    """
    Render the public intake single page app.

    Deliberately not case.utils.react.render_react_page: that helper injects
    staff permission context and dereferences request.user attributes that
    do not exist for AnonymousUser.
    """
    sentry_context = {
        "dsn": settings.SENTRY_JS_DSN or "",
        "environment": settings.ENVIRONMENT or "",
    }
    # Runtime config the SPA reads from window.INTAKE_CONFIG. The Google Maps
    # key powers the address autocomplete (when empty the form falls back to
    # manual address entry); the reCAPTCHA site key guards the no-email contact
    # form.
    intake_config = {
        "googleMapsApiKey": settings.GOOGLE_MAPS_API_KEY or "",
        "recaptchaSiteKey": settings.RECAPTCHA_PUBLIC_KEY or "",
    }
    context = {
        "title": title,
        "react_context": json.dumps(react_context or {}),
        "sentry_context": json.dumps(sentry_context),
        "intake_config": json.dumps(intake_config),
        # The shared navbar hides its "Get free help" call to action here: the
        # visitor is already in the intake form, so the link is redundant.
        "hide_intake_cta": True,
    }
    return render(request, "intake/base.html", context)
