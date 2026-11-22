from wagtail.snippets.models import register_snippet
from wagtail.snippets.views.snippets import SnippetViewSet

from .models import BlacklistEntry


class BlacklistAdmin(SnippetViewSet):
    model = BlacklistEntry
    menu_label = "Blacklist"
    icon = "warning"
    menu_order = 205
    list_display = ("name", "email", "phone", "created_at")
    search_fields = ("name", "email", "phone")


register_snippet(BlacklistAdmin)
