from django import template
from office.shutdown.service import get_shutdown_notice

register = template.Library()


@register.inclusion_tag("web/_notice.html")
def notice():
    return {
        "office_shutdown_notice": get_shutdown_notice(),
    }
