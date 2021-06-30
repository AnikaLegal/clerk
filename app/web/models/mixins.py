from django.http import Http404, HttpResponse
from wagtail.core import hooks
from wagtail.core.models import Site
from django.urls import re_path


# See here for details
# https://docs.wagtail.io/en/stable/advanced_topics/customisation/page_editing_interface.html#limiting-features-in-a-rich-text-field
RICH_TEXT_FEATURES = [
    "h2",
    "bold",
    "italic",  # bold / italic text
    "ol",
    "ul",  # ordered / unordered lists
    "link",  # page, external and email links
]


class NotFoundMixin:
    def serve(request, *args, **kwargs):
        raise Http404("Page does not exist.")


class MultiRootPageMixin:
    public_path = None
    wagtail_slug = None

    def get_private_path(self):
        return f"/cms/pages/{self.wagtail_slug}/"

    def get_url_parts(self, *args, **kwargs):
        site_id, root_url, page_path = super().get_url_parts(*args, **kwargs)
        new_path = None
        if page_path is not None:
            new_path = page_path.replace(self.get_private_path(), self.public_path)

        return site_id, root_url, new_path

    @classmethod
    def as_path(cls, name: str):
        def wagtail_serve_view(request, path):
            """
            Override default Wagtail 'serve' view.
            https://github.com/wagtail/wagtail/blob/main/wagtail/core/views.py#L12
            """
            site = Site.find_for_request(request)
            if not site:
                raise Http404

            path_components = [component for component in path.split("/") if component]

            # Begin hack: before this is Wagtail code.
            path_components = [cls.wagtail_slug] + path_components
            # End hack: after this is Wagtail code.

            page, args, kwargs = site.root_page.localized.specific.route(
                request, path_components
            )

            for fn in hooks.get_hooks("before_serve_page"):
                result = fn(page, request, args, kwargs)
                if isinstance(result, HttpResponse):
                    return result

            return page.serve(request, *args, **kwargs)

        url_prefix = cls.public_path.lstrip("/")
        url_re = f"^{url_prefix}((?:[\w\-]+/)*)$"
        return re_path(url_re, wagtail_serve_view, name=name)
