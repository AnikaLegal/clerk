from django import template
from web.forms import ContactForm

register = template.Library()


@register.simple_tag()
def contact_form():
    return ContactForm()
