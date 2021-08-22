from typing import Optional
from django.template.loader import render_to_string
from django.shortcuts import render

CANCEL_SLUG = "cancel"


class Selector:
    template = "case/snippets/_selector.html"

    slug: str
    default_text: str
    child_views: dict
    options: dict
    render_when: Optional[dict]

    def __init__(self, request):
        self.request = request
        assert self.slug, "slug must be set."
        assert self.default_text, "default_text must be set."
        assert self.child_views, "child_views must be set."
        assert self.options, "options must be set."
        assert (
            CANCEL_SLUG not in self.child_views
        ), f"Child slug '{CANCEL_SLUG}' reserved."
        self.qs_name = f"select-{self.slug}"
        self.id = f"selector-{self.slug}"
        self.target_id = f"selector-target-{self.slug}"
        self.dropdown_id = f"selector-dropdown-{self.slug}"
        self.render_when = self.render_when or {}

    def handle(self, child_slug, *args, **kwargs):
        if self.request.method == "GET":
            child_slug = child_slug or self.request.GET.get(self.qs_name)

        if child_slug == CANCEL_SLUG:
            # Reset the template.
            context = self.get_context()
            return render(self.request, self.template, context)

        child_view = self.child_views.get(child_slug)
        if child_view and self.should_render_child(child_slug):
            child_resp = child_view(self.request, *args, **kwargs)
            is_child_rendered = (
                child_resp.status_code == 200
                and child_resp.headers["Content-Type"] == "text/html; charset=utf-8"
            )
            if is_child_rendered:
                # Append selector dropdown update to the response.
                dropdown_ctx = self.get_context(active_slug=child_slug)
                update_bytes = render_to_string(self.template, dropdown_ctx).encode(
                    "utf-8"
                )
                child_resp._container[0] += update_bytes

            return child_resp

    def render_to_string(self):
        context = self.get_context()
        return render_to_string(self.template, context)

    def should_render_child(self, child_slug: str):
        child_view = self.child_views.get(child_slug)
        if child_view:
            render_when = self.render_when.get(child_slug)
            if render_when and render_when(child_view, self.request):
                return True

        return False

    def get_context(self, active_slug: str = ""):
        options = {
            child_slug: text
            for child_slug, text in self.options.items()
            if self.should_render_child(child_slug)
        }
        return {
            "default_text": self.default_text,
            "active_slug": active_slug,
            "active_slug_text": self.options.get(active_slug),
            "options": options,
            "qs_name": self.qs_name,
            "id": self.id,
            "target_id": self.target_id,
            "dropdown_id": self.dropdown_id,
        }

    def __str__(self):
        return self.render_to_string()