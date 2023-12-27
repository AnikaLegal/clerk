import re

from django.utils.html import strip_tags
from html_sanitizer import Sanitizer

from emails.models import Email


def get_email_html(email: Email) -> str:
    if email.html:
        return sanitizer.sanitize(email.html)
    else:
        text = email.text.replace("\r", "")
        text = re.sub("\n(?!\n)", "<br/>", text)
        return "".join(
            [f"<p>{line}</p>" for line in strip_tags(text).split("\n") if line]
        )


sanitizer = Sanitizer(
    {
        "tags": {
            "a",
            "b",
            "blockquote",
            "br",
            "div",
            "em",
            "h1",
            "h2",
            "h3",
            "hr",
            "i",
            "li",
            "ol",
            "p",
            "span",
            "strong",
            "sub",
            "sup",
            "ul",
            "img",
        },
        "attributes": {
            "a": ("href", "name", "target", "title", "id", "rel", "src", "style")
        },
        "empty": {"hr", "a", "br", "div"},
        "separate": {"a", "p", "li", "div"},
        "whitespace": {"br"},
        "keep_typographic_whitespace": False,
        "add_nofollow": False,
        "autolink": False,
    }
)
