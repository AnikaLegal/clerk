from django import template

register = template.Library()


@register.simple_tag(takes_context=True)
def get_cookie(context, cookie_name):
    request = context["request"]
    result = request.COOKIES.get(cookie_name, '')
    return result
