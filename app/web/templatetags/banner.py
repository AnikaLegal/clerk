from django import template
from web.models import Banner

register = template.Library()
cookie_prefix = "dismiss_banner"


@register.inclusion_tag("web/snippets/_banner.html", takes_context=True)
def banner(context):
    banner = Banner.objects.filter(live=True).last()
    if not banner:
        return {}

    # Don't display the banner if:
    # - The presence of a cookie indicates it has been dismissed already.
    # - The URL the banner is trying to get us to visit is the one being
    #   displayed.
    request = context["request"]
    cookie_name = f"{cookie_prefix}_{banner.pk}"
    if (
        cookie_name in request.COOKIES
        or banner.call_to_action_url == request.build_absolute_uri()
    ):
        return {}

    return {
        "banner": banner,
        # Cookie expires in 24 hours.
        "dismiss_banner_cookie": f"{cookie_name}=true; max-age=86400; Path=/",
        "request": request,
    }
