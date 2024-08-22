import re
from bs4 import BeautifulSoup
from django.conf import settings
from django.utils.html import strip_tags
from django.template.loader import render_to_string
from django.utils.safestring import mark_safe
from html_sanitizer import Sanitizer

from emails.models import Email


def render_email_template(html: str) -> str:
    if html:
        soup = BeautifulSoup(html, parser="lxml", features="lxml")
        for p_tag in soup.find_all("p"):
            p_tag["style"] = "margin:0 0 12px 0;"

        for a_tag in soup.find_all("a"):
            a_tag["style"] = "color:#438fef;text-decoration:underline;"

        html = mark_safe(soup.body.decode_contents())
    else:
        html = ""

    context = {
        "html": html,
        "bucket_url": "https://{bucket}.s3-{region}.amazonaws.com".format(
            bucket=settings.EMAIL_BUCKET_NAME, region=settings.AWS_REGION_NAME
        ),
    }
    return render_to_string("case/email_preview.html", context)


def parse_email_html(email: Email) -> str:
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
