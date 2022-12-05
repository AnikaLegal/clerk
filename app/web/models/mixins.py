from django.http import Http404


# See here for details
# https://docs.wagtail.io/en/stable/advanced_topics/customisation/page_editing_interface.html#limiting-features-in-a-rich-text-field
RICH_TEXT_FEATURES = [
    "h3",
    "bold",
    "italic",  # bold / italic text
    "ol",
    "ul",  # ordered / unordered lists
    "link",  # page, external and email links
]


class NotFoundMixin:
    def serve(request, *args, **kwargs):
        raise Http404("Page does not exist.")
