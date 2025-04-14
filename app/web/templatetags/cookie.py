from django import template

register = template.Library()


@register.simple_tag(takes_context=True)
def get_cookie(context, cookie_name):
    request = context.get("request")
    if request:
        return request.COOKIES.get(cookie_name, "")
    return ""
