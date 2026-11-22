from wagtail.snippets.models import register_snippet
from wagtail.snippets.views.snippets import CreateView, SnippetViewSet

from .models import BlacklistEntry


class BlacklistCreateView(CreateView):
    def save_instance(self):
        self.form.instance.created_by = self.request.user
        return super().save_instance()


class BlacklistAdmin(SnippetViewSet):
    model = BlacklistEntry
    menu_label = "Blacklist"
    icon = "warning"
    menu_order = 205
    list_display = ("name", "email", "phone", "created_by", "created_at")
    search_fields = ("name", "email", "phone")
    add_view_class = BlacklistCreateView


register_snippet(BlacklistAdmin)
