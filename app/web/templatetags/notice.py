from django import template
from office.closure.service import get_closure_notice

register = template.Library()


@register.inclusion_tag("web/_notice.html")
def notice():
    return {
        "office_closure_notice": get_closure_notice(),
    }
