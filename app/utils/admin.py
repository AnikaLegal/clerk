import json

from django.utils.html import format_html
from django.urls import reverse
from django.utils.safestring import mark_safe
from pygments import highlight
from pygments.formatters import HtmlFormatter
from pygments.lexers import JsonLexer


def admin_change_url(obj):
    app_label = obj._meta.app_label
    model_name = obj._meta.model.__name__.lower()
    return reverse("admin:{}_{}_change".format(app_label, model_name), args=(obj.pk,))


def admin_link(attr: str, short_description: str, empty_description: str = "-"):
    def wrap(func):
        def field_func(self, obj):
            related_obj = getattr(obj, attr)
            if related_obj is None:
                return empty_description
            url = admin_change_url(related_obj)
            return format_html('<a href="{}">{}</a>', url, func(self, related_obj))

        field_func.short_description = short_description
        field_func.allow_tags = True
        return field_func

    return wrap


def dict_to_json_html(data):
    json_str = json.dumps(data, sort_keys=True, indent=2)
    formatter = HtmlFormatter(style="colorful")
    highlighted = highlight(json_str, JsonLexer(), formatter)
    style = "<style>" + formatter.get_style_defs() + "</style><br>"
    return mark_safe(style + highlighted)
