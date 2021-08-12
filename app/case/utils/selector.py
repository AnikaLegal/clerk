from django.template.loader import render_to_string
from django.shortcuts import render

CANCEL_SLUG = "cancel"


class Selector:
    template = "case/snippets/_selector.html"
    dropdown_template = "case/snippets/_selector.html"

    def __init__(self, slug: str, default_text: str, child_views: dict, options: dict):
        self.slug = slug
        assert CANCEL_SLUG not in child_views, f"Child slug '{CANCEL_SLUG}' reserved."
        self.default_text = default_text
        self.child_views = child_views
        self.options = options
        self.qs_name = f"select-{self.slug}"
        self.id = f"selector-{self.slug}"
        self.target_id = f"selector-target-{self.slug}"
        self.dropdown_id = f"selector-dropdown-{self.slug}"

    def handle(self, request, child_slug, *args, **kwargs):
        if request.method == "GET":
            child_slug = child_slug or request.GET.get(self.qs_name)

        if child_slug == CANCEL_SLUG:
            # Reset the template.
            context = self.get_context()
            return render(request, self.template, context)

        child_view = self.child_views.get(child_slug)
        if child_view:
            child_resp = child_view(request, *args, **kwargs)
            is_child_rendered = (
                child_resp.status_code == 200
                and child_resp.headers["Content-Type"] == "text/html; charset=utf-8"
            )
            if is_child_rendered:
                # Append selector dropdown update to the response.
                dropdown_ctx = self.get_context(active_slug=child_slug)
                update_bytes = render_to_string(
                    self.dropdown_template, dropdown_ctx
                ).encode("utf-8")
                child_resp._container[0] += update_bytes

            return child_resp

    def render_to_string(self):
        context = self.get_context()
        return render_to_string(self.template, context)

    def get_context(self, active_slug: str = ""):
        return {
            "default_text": self.default_text,
            "active_slug": active_slug,
            "active_slug_text": self.options.get(active_slug),
            "options": self.options,
            "qs_name": self.qs_name,
            "id": self.id,
            "target_id": self.target_id,
            "dropdown_id": self.dropdown_id,
        }

    def __str__(self):
        return self.render_to_string()