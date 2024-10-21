from django import template
from web.models import Banner

register = template.Library()


@register.inclusion_tag("web/snippets/_banner.html", takes_context=True)
def banner(context):
    return {
        "banner": Banner.objects.last(),
        "request": context["request"],
    }
