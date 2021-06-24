from django import template
from django.conf import settings

register = template.Library()


@register.inclusion_tag("web/_analytics.html")
def analytics():
    return {
        "GOOGLE_ANALYTICS_ID": settings.GOOGLE_ANALYTICS_ID,
        "FACEBOOK_PIXEL_ID": settings.FACEBOOK_PIXEL_ID,
    }
